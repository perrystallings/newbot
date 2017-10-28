def respond(sender_id, message_text, attachment_type, attachment_url, postback, quick_reply, context):
    from bot.lib.material import create_material
    from bot.lib.project import update_project
    from .utilities import send_date_picker
    material = create_material(sender_id=sender_id, url=attachment_url, file_type=attachment_type)
    update_project(sender_id=sender_id, project_id=context["project_id"], material_id=str(material.id))
    new_context = context
    conversation = dict(name='create_project', stage='add_due_date')
    response = send_date_picker(sender_id=sender_id)
    return response, new_context, conversation


def validate(sender_id, message_text, attachment_type, postback, quick_reply):
    if attachment_type in ['image']:
        return True, dict(message_text='')
    else:
        return False, dict(message_text='Please take a photo to proceed')