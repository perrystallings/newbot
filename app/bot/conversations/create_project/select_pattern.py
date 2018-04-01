def respond(sender_id, message_text, attachment_type, attachment_url, postback, quick_reply, context):
    from bot.lib.project import update_project
    from bot.lib.maker import get_maker_id
    from bot.models import Material
    """Takes in ``sender_id``, ``postback``= supply id,
     ``context`` = project id and updates project and sends a reponse.

    :param str sender_id: The unique id created by facebook and the current facebook's sender's ID
    :param str postback: a reponse sent from the user clicking a button (optional, defaults to None)
    :param dict context: attributes sent between conversation in the case project_id
    :param str message_text: Any text written in the chat interface (optional, defaults to None)
    :param str attachment_type: dentifies attachment type i.e photo (optional, defaults to None)
    :param str attachment_url: The location of the attachment (optional, defaults to None)
    :param str quick_reply: an automatic reply (optional, defaults to None)

    :returns: ``reponse``a dict with the next message to move the conversation
    ``new_context`` same context as before, and ``coverstation`` dict containing
    the next stage and task for the the bot
    """

    update_project(sender_id=sender_id, project_id=context["project_id"], pattern_id=postback)
    new_context = context
    conversation = dict(name='create_project', stage='material_menu')
    response = dict(message_text="Great! Now you want to add a new material or select an existing one?",
                    quick_replies=[
                        {
                            "content_type": "text",
                            "title": "New Material",
                            "payload": "ADD_MATERIAL",
                        },
                    ]
                    )
    if Material.objects.filter(maker_id=get_maker_id(sender_id=sender_id)).count() > 0:
        response['quick_replies'].append(
            {
                "content_type": "text",
                "title": "Select Material",
                "payload": "SELECT_MATERIAL",
            }
        )
    return response, new_context, conversation


def validate(sender_id, message_text, attachment_type, postback, quick_reply):
    """Boolean takes in ``postback``= postback of supply id
    and determines if the message type is valid.

    :param str sender_id: The unique id created by facebook and the current facebook's sender's ID
    :param str postback: a reponse sent from the user clicking a button 
    :param str message_text: Any text written by the send in the chat interface (optional, defaults to None)
    :param str attachment_type: Identifies attachment type i.e photo (optional, defaults to None)
    :param str quick_reply: an automatic (optional, defaults to None)

    :returns: Booleen and a dict with message text if the message is not valid """
    if postback:
        return True, dict(message_text='')
    else:
        return False, dict(message_text='Please select from the menu.')

        # TODO probably need to see what happen with other things here
