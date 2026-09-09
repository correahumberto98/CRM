"""Contact-specific catalogues; independent of deal pipeline stages."""

CONTACT_SOURCES = (
    ("META", "Meta"),
    ("GOOGLE", "Google"),
    ("TIKTOK", "TikTok"),
    ("ORGANIC", "Organic"),
    ("CALL", "Call"),
    ("CUSTOMER_REFERAL", "Customer Referal"),
    ("EMPLOYER_REFERAL", "Employer Referal"),
    ("WALK_IN", "Walk In"),
)
CONTACT_STAGES = (
    ("LEAD", "Lead"),
    ("FOLLOW_UP", "Follow Up"),
    ("QUALIFIED", "Qualified"),
    ("NOT_QUALIFIED", "Not Qualified"),
    ("LOST", "Lost"),
)
COMMUNICATION_CHANNELS = (
    ("SMS", "SMS"),
    ("CALL", "Call"),
    ("EMAIL", "Email"),
)
