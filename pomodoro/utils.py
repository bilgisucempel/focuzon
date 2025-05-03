from datetime import timedelta


def get_total_duration(sessions):
    """
    Verilen Pomodoro oturumlarının toplam süresini hesaplar.
    :param sessions: QuerySet (Tamamlanmış oturum listesi)
    :return: timedelta (Toplam süre)
    """
    total = timedelta()
    for session in sessions:
        if session.duration:
            total += session.duration
    return total


def format_duration(duration):
    """
    timedelta nesnesini dakika cinsinden okunabilir formata çevirir.
    :param duration: timedelta
    :return: string (örn: '125 dakika')
    """
    if not duration:
        return "0 dakika"

    total_minutes = int(duration.total_seconds() // 60)
    return f"{total_minutes} dakika"

