import requests

def get_max_size(sizes):
  max_val=0
  max_size={}
  for size in sizes:
    if int(size.get("height"))*int(size.get("width"))>=max_val:
      max_size=size
  return max_size

def parse_attachments(attachments:list) -> list:
  result=[]
  for attachment in attachments:
    attachment_type=attachment.get("type")
    match attachment_type:
      case "photo":
        attachment=attachment.get("photo")
        result.append({
          "photo":f"photo{attachment.get("owner_id")}_{attachment.get("id")}_{attachment.get("access_key")}",
          "url":get_max_size(attachment.get("sizes")).get("url")
          })
      case "audio":
        attachment=attachment.get("audio")
        result.append({
          "audio":f"audio{attachment.get("owner_id")}_{attachment.get("id")}_{attachment.get("access_key")}"
          })
      case "video":
        attachment=attachment.get("video")
        result.append({
          "video":f"video{attachment.get("owner_id")}_{attachment.get("id")}_{attachment.get("access_key")}"
          })
      case "doc":
        attachment=attachment.get("doc")
        match list(attachment.get("preview",{"no":"no"}).keys())[0]:
          case "photo":
            url=requests.get(attachment.get("url",""),timeout=5).url
            result.append({"gif":f"{url}"})
          case _:
            url=requests.get(attachment.get("url",""),timeout=5).url
            result.append({"graffiti":f"{url}"})
      case "graffiti":
        attachment=attachment.get("graffiti")
        url=requests.get(attachment.get("url",""),timeout=5).url
        result.append({"graffiti":f"{url}"})
      case "sticker":
        attachment=attachment.get("sticker")
        url=get_max_size(attachment.get("images",[])).get("url","")
        result.append({"sticker":f"{url}"})
      case "audio_message":
        attachment=attachment.get("audio_message")
        url=attachment.get("link_mp3","")
        result.append({"audio_message":f"{url}"})
      case "poll":
        attachment=attachment.get("poll")
        result.append({"poll":f"{attachment.get("owner_id")}_{attachment.get("id")}"})
      case "_":
        pass
  return result
