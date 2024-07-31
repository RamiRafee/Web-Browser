def show(body):
    """
    Display the body content by filtering out HTML tags and replacing entities.
    
    Args:
        body (str): The body content to display.
    """
    in_tag = False
    entity_buffer = ""
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            if c == "&":
                entity_buffer = "&"
            elif entity_buffer:
                entity_buffer += c
                if entity_buffer == "&lt;":
                    print("<", end="")
                    entity_buffer = ""
                elif entity_buffer == "&gt;":
                    print(">", end="")
                    entity_buffer = ""
                elif entity_buffer[-1] == ";":
                    # If we encounter an unknown entity, print it as is
                    print(entity_buffer, end="")
                    entity_buffer = ""
            else:
                print(c, end="")
        else:
            # Print the contents inside tags as is
            entity_buffer = ""
