system_prompt = """
You are a helpful assistant that generates deatiled  summery of given inforamtion about comapny in simaple format in the tone of a paul graham.
"""
def tag_string_to_dict(tags):
    tags = tags.split(";")
    tags = [tag.split(":")[1] for tag in tags]
    return tags


def user_prompt(markdown,Name,Headline,Batch,Description,Activity_Status,Website,Founded_Date,Team_Size,Location,Group_Partner,Tags):
    tags = tag_string_to_dict(Tags)
    output = f"""
    Name of the Company is {Name}
    missson of the {Name} is {Headline}
    The {Name} initaly started as {Description} Website of the Company is {Website}
    it was founded in {Founded_Date} and is part of Y Combinator Batch {Batch}
    Locaated in {Location} it has Team of {Team_Size} employees
    They have {Group_Partner} as their Group Partner
    it is tagged as {tags}
    The Company is currently Doing following things: {markdown}
    
    
    """
    return output

