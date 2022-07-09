class TimeFrame(object):
    (Ticks, MicroSeconds, Seconds, Minutes,
     Days, Weeks, Months, Years, NoTimeFrame) = range(1, 10)

    Names = ['', 'Ticks', 'MicroSeconds', 'Seconds', 'Minutes',
             'Days', 'Weeks', 'Months', 'Years', 'NoTimeFrame']

    names = Names  # support old naming convention

    @classmethod
    def getname(cls, tframe, compression=None):
        tname = cls.Names[tframe]
        if compression > 1 or tname == cls.Names[-1]:
            return tname  # for plural or 'NoTimeFrame' return plain entry

        # return singular if compression is 1
        return cls.Names[tframe][:-1]

    @classmethod
    def TFrame(cls, name):
        return getattr(cls, name)

    @classmethod
    def TName(cls, tframe):
        return cls.Names[tframe]

    @classmethod
    def get_interval_in_minutes(cls, timeframe, compression):
        total_minutes = compression
        if timeframe == TimeFrame.Minutes:
            total_minutes = compression
        elif timeframe == TimeFrame.Days:
            total_minutes = compression * 24 * 60
        elif timeframe == TimeFrame.Weeks:
            total_minutes = compression * 24 * 60 * 7

        return total_minutes
