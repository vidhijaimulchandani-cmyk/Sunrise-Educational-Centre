import random
import string
import datetime
from auth_handler import create_live_class, format_ist_time, get_current_ist_time

def main() -> None:
    class_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    pin = ''.join(random.choices(string.digits, k=4))
    # Schedule for current time (now)
    scheduled_time = format_ist_time(get_current_ist_time())

    new_id = create_live_class(
        class_code=class_code,
        pin=pin,
        meeting_url='https://meet.jit.si/demo-class-11',
        topic='Demo Live Class - Class 11 (Applied/Core Overview)',
        description='Intro session covering syllabus outline and platform walkthrough',
        status='scheduled',
        scheduled_time=scheduled_time,
        target_class='11',
        class_stream='applied',
        class_type='lecture',
        paid_status='unpaid',
        subject='maths',
        teacher_name='Mohit sir'
    )

    print({'created_id': new_id, 'class_code': class_code, 'pin': pin, 'scheduled_time': scheduled_time})

if __name__ == '__main__':
    main()


