
def get_tags():
  with open("website/tags.txt","r") as file:
    tags = file.read().splitlines()
    
  return tags