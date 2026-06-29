from fastapi import APIRouter, status

router = APIRouter()

@router.get("/examples", status_code=status.HTTP_200_OK)
def get_examples():
    """
    Return a list of standard emotional prompts to guide users.
    """
    return {
        "examples": [
            "Feeling low, need something that lifts me slowly",
            "Melancholy but hopeful",
            "Peaceful after a long day",
            "Angry but want to calm down",
            "Music that feels like rain after a difficult day",
            "Quiet confidence"
        ]
    }
