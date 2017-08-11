﻿"""
Configure parameters
"""

sequence_path = r"D:\seqs\\"
skvz_bin = r"D:\bins\skvz_v3.exe"
shm_bin = r"D:\bins\shm.exe"
results = r"D:\r\notvenctester\\"

exel_template = r"D:\dev\notvenctester\BD-rate-template.xlsm"

#Sequence list. Use Class slices to get specific groups. Sequence_names has simplified names for each sequence
hevc_A = slice(0,2)
hevc_B = slice(2,7)
hevc_C = slice(7,11)
hevc_D = slice(11,15)
hevc_E = slice(15,18)
hevc_F = slice(18,22)
sequences = [
    (r"hevc-A\PeopleOnStreet_2560x1600_30.yuv",),
    (r"hevc-A\Traffic_2560x1600_30.yuv",),
    (r"hevc-B\BasketballDrive_1920x1080_50_500.yuv",),
    (r"hevc-B\BQTerrace_1920x1080_60_600.yuv",),
    (r"hevc-B\Cactus_1920x1080_50.yuv",),
    (r"hevc-B\Kimono1_1920x1080_24.yuv",),
    (r"hevc-B\ParkScene_1920x1080_24.yuv",),
    (r"hevc-C\BasketballDrill_832x480_50_500.yuv",),
    (r"hevc-C\BQMall_832x480_60_600.yuv",),
    (r"hevc-C\PartyScene_832x480_50_500.yuv",),
    (r"hevc-C\RaceHorses_832x480_30.yuv",),
    (r"hevc-D\BasketballPass_416x240_50_500.yuv",),
    (r"hevc-D\BlowingBubbles_416x240_50_500.yuv",),
    (r"hevc-D\BQSquare_416x240_60_600.yuv",),
    (r"hevc-D\RaceHorses_416x240_30.yuv",),
    (r"hevc-E\FourPeople_1280x720_60.yuv",),
    (r"hevc-E\Johnny_1280x720_60.yuv",),
    (r"hevc-E\KristenAndSara_1280x720_60.yuv",),
    (r"hevc-F\BasketballDrillText_832x480_50_500.yuv",),
    (r"hevc-F\ChinaSpeed_1024x768_30.yuv",),
    (r"hevc-F\SlideEditing_1280x720_30.yuv",),
    (r"hevc-F\SlideShow_1280x720_20.yuv",),
    ]
sequence_names = [
    "PeopleOnStreet",
    "Traffic",
    "BasketballDrive",
    "BQTerrace",
    "Cactus",
    "Kimono1",
    "ParkScene",
    "BasketballDrill",
    "BQMall",
    "PartyScene",
    "RaceHorsesC",
    "BasketballPass",
    "BlowingBubbles",
    "BQSquare",
    "RaceHorsesD",
    "FourPeople",
    "Johnny",
    "KristenAndSara",
    "BasketballDrillText",
    "ChinaSpeed",
    "SlideEditing",
    "SlideShow",
    ]

class_sequence_names = [
    "hevc-A_PeopleOnStreet",
    "hevc-A_Traffic",
    "hevc-B_BasketballDrive",
    "hevc-B_BQTerrace",
    "hevc-B_Cactus",
    "hevc-B_Kimono1",
    "hevc-B_ParkScene",
    "hevc-C_BasketballDrill",
    "hevc-C_BQMall",
    "hevc-C_PartyScene",
    "hevc-C_RaceHorses",
    "hevc-D_BasketballPass",
    "hevc-D_BlowingBubbles",
    "hevc-D_BQSquare",
    "hevc-D_RaceHorses",
    "hevc-E_FourPeople",
    "hevc-E_Johnny",
    "hevc-E_KristenAndSara",
    "hevc-F_BasketballDrillText",
    "hevc-F_ChinaSpeed",
    "hevc-F_SlideEditing",
    "hevc-F_SlideShow",
    ]