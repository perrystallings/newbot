from celery import shared_task

@shared_task()
def route_message(sender_id, message_text, quick_reply, postback, attachment_url, attachment_type):
    if isinstance(postback, str) and postback.upper() in ["ADD_PROJECT_PAYLOAD", "UPDATE_PROJECT_PAYLOAD",
                                                          "ADD_PATTERN_PAYLOAD", "ADD_MATERIAL_PAYLOAD"]:
        process_menu_selection(sender_id, postback)
    elif isinstance(postback, str) and postback.upper() == "START":
        welcome_new_user(sender_id)
    else:
        process_message(sender_id, message_text, quick_reply, postback, attachment_url, attachment_type)


def process_message(sender_id, message_text, quick_reply, postback, attachment_url, attachment_type):
    from common.facebook import send_message
    from bot.models import Maker
    from bot.lib.maker import get_maker_id, update_maker
    from bot.lib.conversation import load_conversation
    send_message(sender_id=sender_id, action='mark_seen')
    maker = Maker.objects.prefetch_related("conversation_stage__conversation").get(id=get_maker_id(sender_id=sender_id))
    conversation = load_conversation(
        conversation_name=maker.conversation_stage.conversation.name,
        stage_name=maker.conversation_stage.name
    )

    valid, failure_response = conversation.validate(
        sender_id=sender_id,
        message_text=message_text,
        quick_reply=quick_reply,
        postback=postback,
        attachment_type=attachment_type)
    if not valid:
        send_message(
            sender_id=sender_id,
            text=failure_response.get('message_text'),
            buttons=failure_response.get('buttons'),
            attachment=failure_response.get('attachment'),
            quick_replies=failure_response.get('quick_replies')
        )
    else:
        send_message(sender_id=sender_id, action='typing_on')
        response, context, next_conversation = conversation.respond(
            sender_id=sender_id,
            message_text=message_text,
            quick_reply=quick_reply,
            postback=postback,
            attachment_type=attachment_type,
            attachment_url=attachment_url,
            context=maker.context
        )
        r = send_message(
            sender_id=sender_id,
            text=response.get('message_text'),
            buttons=response.get('buttons'),
            attachment=response.get('attachment'),
            quick_replies=response.get('quick_replies')
        )
        update_maker(sender_id=sender_id, context=context, conversation=next_conversation)
    return valid


def process_menu_selection(sender_id, postback):
    from bot.lib.maker import update_maker, get_maker_id
    from common.facebook import send_message
    from bot.models import Project
    context = dict()
    message_text = None
    conversation = dict()
    attachment = None
    if postback == "ADD_PROJECT_PAYLOAD":
        conversation = dict(name="create_project", stage="name_project")
        # TODO handle when a user has too many projects
        projects = Project.objects.filter(maker_id=get_maker_id(
            sender_id=sender_id)).filter(complete=True).exclude(finished=True)
        if projects.count() == 6:
            message_text = "Sorry it looks like you have max out your new project. You need to finish something before you can add anything new"
        else:
            message_text = "Great! What would you like to call this project?"

    elif postback == "UPDATE_PROJECT_PAYLOAD":
        conversation = dict(name="update_project_status", stage="project_selection")
        projects = Project.objects.filter(maker_id=get_maker_id(sender_id=sender_id)).filter(complete=True).exclude(finished=False)
        if projects.count() > 0:
            attachment = format_project_carousel(projects=projects)
        else:
            message_text = "It looks like you don't have any active projects. Add a project to get started!"

    elif postback in ["ADD_PATTERN_PAYLOAD", "ADD_MATERIAL_PAYLOAD"]:
        conversation = dict(name="create_supplies", stage="add_image")
        context = dict(type=postback.split("_")[1].lower())
        message_text = "Awesome! Please take a photo of the {0} to get started".format(context['type'])

    update_maker(sender_id=sender_id, conversation=conversation, context=context)
    send_message(sender_id=sender_id, text=message_text, attachment=attachment)


def welcome_new_user(sender_id):
    from bot.lib.maker import create_maker
    from common.facebook import send_message
    create_maker(sender_id=sender_id)
    send_message(sender_id=sender_id, text="Welcome to CraftyBot select from menu to get started")


def format_project_carousel(projects):
    from common.utilities import get_file_url
    carousel = {
            "type":"template",
            "payload":{
            "template_type":"generic",
            "elements":[]
        }
    }
    for project in projects[0:10]:
        element = {
            "title": project.name,
            "subtitle": " ".join(["#{0}".format(tag.name) for tag in project.tags.all()]),
            "image_url": get_file_url(project.materials.first().files.first()),
            "buttons": [
                {
                    "title": "Select",
                    "type": "postback",
                    "payload": str(project.id)
                }
            ]
        }
        if len(element['subtitle'])> 30:
            element.pop('subtitle')
        if len(element['title'])> 30:
            element['title'] = element['title'][:30] + '...'
        carousel['payload']['elements'].append(
            element
        )
    return carousel
