from aiocache import Cache
from fastapi import FastAPI, Response
from pydantic import BaseModel


class PetRegistration(BaseModel):
    name: str
    owner: str


# @kloto::expose {
#    id = "pet-api"
#    target = "public"
# }
petsByOwner = Cache(Cache.MEMORY)

# @klotho::expose {
#   id = "pet-api"
#   target = "public"
# }
app = FastAPI()

@app.post("/pets")
async def register_pet(registration: PetRegistration):
    """
    Associate a pet with an owner.
    """
    name = registration.name
    owner = registration.owner
    
    # get the list of pets for the owner currently registered pets
    pets = await petsByOwner.get(owner, default=[])
    
    # adds the pet to the owner's list of pets and stores the updated list
    pets.append(name)
    await petsByOwner.set(owner, pets)
    
    return f"Added {name} to {owner}'s pets."


@app.get("/owners/{owner}/pets")
async def get_owner_pets(owner: str, response: Response):
    """
    Gets all pets registered to the supplied owner
    """
    pets = await petsByOwner.get(owner, default=[])
    if not pets:
        response.status_code = 404
        return f"No pets found for {owner}"
    return pets