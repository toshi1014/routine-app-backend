import config

def get_badge(followers_num):
    badge = "noBadge"
    if followers_num >= config.BADGE_L1:
        badge = "l1"
    if followers_num >= config.BADGE_L2:
        badge = "l2"
    if followers_num >= config.BADGE_L3:
        badge = "l3"
    return badge