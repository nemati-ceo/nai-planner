import django.dispatch

# Fired when a reminder's remind_at time is reached.
# Sender: PlannerItem instance
# Kwargs: user (User instance), item (PlannerItem instance)
reminder_due = django.dispatch.Signal()
