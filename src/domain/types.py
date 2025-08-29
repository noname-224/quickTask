# from datetime import datetime
# from typing import Annotated
#
# from sqlalchemy import text
# from sqlalchemy.orm import mapped_column


# created_at = Annotated[
#     datetime,
#     mapped_column(
#         server_default=text("TIMEZONE('utc', now())")
#     )
# ]
# updated_at = Annotated[
#     datetime,
#     mapped_column(
#         server_default=text("TIMEZONE('utc', now())"),
#         onupdate=datetime.utcnow,
#         )
# ]


TaskId = int
UserId = int
ChatId = int
MessageId = int

message_types = ['audio', 'photo', 'voice', 'video', 'document', 'text', 'location', 'contact', 'sticker', 'commands']