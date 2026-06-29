import structlog
from typing import Optional
from fastapi import APIRouter, Depends, Request, status
from app.models.prompt import PromptRequest
from app.models.queue import VibeQueue
from app.middleware.rate_limiter import get_optional_user, get_client_ip
from app.pipeline.orchestrator import PipelineOrchestrator
from app.utils.errors import RateLimitException, ValidationException, PipelineException, VibeException

logger = structlog.get_logger()
router = APIRouter()
orchestrator = PipelineOrchestrator()

@router.post("/vibe", response_model=VibeQueue, status_code=status.HTTP_200_OK)
def generate_vibe_queue(
    request: Request,
    body: PromptRequest,
    user: Optional[dict] = Depends(get_optional_user),
    client_ip: str = Depends(get_client_ip)
):
    """
    Accept user prompt, run the AI pipeline, and return the generated Vibe Queue.
    Enforces hourly limits for signed-in users and trial limits for anonymous clients.
    """
    is_auth = user is not None
    identifier = user["id"] if is_auth else client_ip
    
    # Retrieve request_id from structlog context vars if available
    context_vars = structlog.contextvars.get_contextvars()
    req_id = context_vars.get("request_id")

    logger.info(
        "Received vibe queue generation request.",
        prompt=body.prompt,
        identifier=identifier,
        is_authenticated=is_auth,
        request_id=req_id
    )

    try:
        # Run orchestrator
        vibe_queue = orchestrator.run(
            prompt=body.prompt,
            identifier=identifier,
            is_authenticated=is_auth,
            request_id=req_id
        )
        
        # Raise ValidationException for critically low confidence (gibberish/nonsensical prompts)
        if vibe_queue.confidence <= 0.2:
            raise ValidationException(
                message="I couldn't quite understand that. Try describing how you're feeling or use the suggested prompts.",
                suggestion="Try prompts like 'Feeling low, need something that lifts me slowly' or select one of the suggested prompts above!"
            )
            
        return vibe_queue
    except ValueError as val_err:
        err_msg = str(val_err)
        logger.warning("Pipeline validation or rate limit error.", error=err_msg)
        
        # Map specific orchestrator messages to exception types
        if "limit reached" in err_msg or "limit exceeded" in err_msg:
            raise RateLimitException(message=err_msg)
        elif "cannot be empty" in err_msg or "500 characters" in err_msg:
            raise ValidationException(message=err_msg)
        else:
            raise PipelineException(message=err_msg)
    except VibeException as vibe_err:
        # Re-raise known custom exceptions directly
        raise vibe_err
    except Exception as e:
        logger.error("Unexpected pipeline execution error.", error=str(e))
        raise PipelineException(message=f"A pipeline execution error occurred: {str(e)}")

