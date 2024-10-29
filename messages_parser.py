import attachments_parser
from datetime import datetime
profiles={}

def parse_profiles(profiles_list:list):
  global profiles
  new_profiles_dict={}
  for profile in profiles_list:
    name=f"{profile.get("first_name","")} {profile.get("last_name","")}"
    new_profiles_dict.update({profile.get("id"):name})
  profiles.update(new_profiles_dict)

def parse_messages(message:dict):
  attachments=attachments_parser.parse_attachments(message.get("attachments",[]))
  match message.get("action",{}).get("type",""):
    case "chat_photo_update":
      attachments.append({"chat_photo_update"})
    case "chat_photo_remove":
      attachments.append({"chat_photo_remove"})
    case "chat_create":
      attachments.append({"chat_create":message.get("action",{}).get("text","")})
    case "chat_title_update":
      attachments.append({"chat_title_update":message.get("action",{}).get("text","")})
    case "chat_kick_user":
      attachments.append({"chat_kick_user":message.get("action",{}).get("member_id","0")})
    case "chat_pin_message":
      attachments.append({"chat_pin_message":message.get("action",{}).get("conversation_message_id","0")})
    case "chat_unpin_message":
      attachments.append({"chat_unpin_message":message.get("action",{}).get("conversation_message_id","0")})
    case "chat_invite_user_by_link":
      attachments.append({"chat_invite_user_by_link":message.get("action",{}).get("member_id","0")})
    case "chat_invite_user":
      attachments.append({"chat_invite_user":message.get("action",{}).get("member_id","0")})
  reactions=[]
  for reaction in message.get("reactions",[]):
    reactions.append({reaction.get("reaction_id",0):reaction.get("user_ids",[])})
  if message.get("reply_message",{}):
    attachments.append({"reply_message":message.get("reply_message",{}).get("conversation_message_id",0)})
  dtime=datetime.fromtimestamp(message.get("date",""))
  return {"id":message.get("conversation_message_id",0),"name":profiles.get(message.get("from_id",0),"Unknown"),"user_id":"id"+str(message.get("from_id","0")),"time":str(dtime.strftime("%H:%M:%S")),"date":str(dtime.strftime("%d.%m.%Y")),"message":message.get("text",""),"reactions":reactions,"attachments":attachments}
