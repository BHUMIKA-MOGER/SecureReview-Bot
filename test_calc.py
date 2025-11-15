def remove_duplicates_in_place(data: list) -> list:
    """
    ATTENTION: This function contains a bug!
    It attempts to remove duplicates from a list in-place by iterating
    over a set of elements and removing them from the list if found.
    This approach will skip elements due to index changes.
    """
    
    seen = set()
    
    # Iterate through the list and try to remove duplicates
    for element in data: 
        if element in seen:
            # BUG: Removing an element while iterating shifts subsequent 
            # elements, causing the loop to skip the next item.
            data.remove(element) 
        else:
            seen.add(element)
            
    return data

# Example of the error:
# original_list = [1, 2, 2, 3, 4, 4, 5]
# result = remove_duplicates_in_place(original_list) 
# The expected result is [1, 2, 3, 4, 5], but the actual result 
# will still contain some duplicates, like [1, 2, 3, 4, 5].