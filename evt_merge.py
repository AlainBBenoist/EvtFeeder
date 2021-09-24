
def evt_merge(event, new_event):
    # Check missing fields
    fields = ['cost', 'evt_media']
    for field in fields :
        if field in new_event and field not in event:
            event[field] = new_event[field]
    return event

if __name__ == '__main__' :
    event = {'name' : 'Premier évenement', 'description' : 'Ceci décrit l\'évenement', }
    event2 = {'cost' : '3', 'evt_media' : 'https://dibutade.fr/wp-content/toto.jpg', 'other_field' : 'toto'}

    evt = evt_merge(event, event2)
    print(evt)
    print(event2.update(event)) # ONLY PYTHON 3.9
