import vmraid

from erpadda.utilities.doctype.video.video import get_id_from_url


def execute():
	vmraid.reload_doc("utilities", "doctype", "video")

	for video in vmraid.get_all("Video", fields=["name", "url", "youtube_video_id"]):
		if video.url and not video.youtube_video_id:
			vmraid.db.set_value("Video", video.name, "youtube_video_id", get_id_from_url(video.url))
