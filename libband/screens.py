from enum import IntEnum


class BandScreens(IntEnum):
    Settings = 0
    Home = 1
    Me = 2
    Timer = 3
    Exercise = 4
    RawData = 5
    DebugControl = 6
    DebugInfo = 7
    InteractiveTouch = 8
    SimpleTouch = 9
    TestWidget = 10
    Oobe = 11
    OobeBoot = 12
    OobeCharging = 13
    OobeChargedBoot = 14
    OobeLanguageSelect = 15
    OobeWelcome = 16
    OobeBtPreSync = 17
    OobeBtSync = 18
    OobeBtPaired = 19
    OobeUpdates = 20
    OobeAlmostThere = 21
    OobePressButtonToStart = 22
    DebugStrip = 23
    SettingPower = 24
    SettingBiosensors = 25
    SettingConnection = 26
    SettingAccessability = 27
    SettingGlance = 28
    SettingGeneral = 29
    SettingUtilities = 30
    SettingDND = 31
    SettingAirplane = 32
    TextMessage = 33
    FontTest = 34
    RunStart = 35
    RunGpsChoice = 36
    RunGpsSearch = 37
    RunReadyToStart = 38
    RunInProgress = 39
    RunPaused = 40
    RunCompleted = 41
    Calendar = 42
    Sleep = 43
    SleepTrack = 44
    SleepInProgress = 45
    SleepPaused = 46
    SleepCompleted = 47
    SleepReadyToSleep = 48
    Call = 49
    BatteryDie = 50
    DebugDayClassification = 51
    DebugLogFile = 52
    TouchSensor = 53
    Syncing = 54
    SyncingAutoDismiss = 55
    Workout = 56
    WorkoutStart = 57
    WorkoutReadyToStart = 58
    WorkoutInProgress = 59
    WorkoutPaused = 60
    WorkoutCompleted = 61
    DebugGsrContact = 62
    GuidedWorkout = 63
    GuidedWorkoutLoad = 64
    GuidedWorkoutStart = 65
    GuidedWorkoutCurrentExercise = 66
    GuidedWorkoutIntersitial = 67
    GuidedWorkoutPaused = 68
    GuidedWorkoutCompleted = 69
    TimerTile = 70
    StopwatchRunning = 71
    StopwatchPaused = 72
    AlarmSetScreen = 73
    RunHowYouFelt = 74
    RunHowYouFeltConfirmation = 75
    DebugGps = 76
    WorkoutHowYouFelt = 77
    SleepHowYouFelt = 78
    RunCountdown = 79
    SettingsFromSubscreen = 80
    TimerTileFromSubscreen = 81
    DebugStripFromSubscreen = 82
    DebugBtConfig = 83
    HomeResetScroll = 84
    Resetting = 85
    Goodbye = 86
    Keyboard = 87
    NotificationDataView = 88
    NumScreenIds = 89
