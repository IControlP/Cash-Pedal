# vehicle_database_p.py - Manufacturers starting with 'P'
# Comprehensive vehicle database with accurate trim availability and pricing by year

MANUFACTURERS_P = {
    'Porsche': {
        '911': {
            'production_years': (2000, 2025),
            'trims_by_year': {
                2000: {'911 Carrera': 70000, '911 Carrera 4': 76000, '911 Turbo': 125000},
                2001: {'911 Carrera': 71000, '911 Carrera 4': 77000, '911 Turbo': 126000, '911 Carrera Cabriolet': 78000},
                2002: {'911 Carrera': 72000, '911 Carrera 4': 78000, '911 Turbo': 127000, '911 Carrera Cabriolet': 79000, '911 Carrera 4 Cabriolet': 85000},
                2003: {'911 Carrera': 73000, '911 Carrera 4': 79000, '911 Turbo': 128000, '911 Carrera Cabriolet': 80000, '911 Carrera 4 Cabriolet': 86000},
                2004: {'911 Carrera': 74000, '911 Carrera 4': 80000, '911 Turbo': 129000, '911 Carrera Cabriolet': 81000, '911 Carrera 4 Cabriolet': 87000},
                2005: {'911 Carrera': 75240, '911 Carrera 4': 81240, '911 Turbo': 129840, '911 Carrera Cabriolet': 82240, '911 Carrera 4 Cabriolet': 88240},
                2006: {'911 Carrera': 76240, '911 Carrera 4': 82240, '911 Turbo': 130840, '911 Carrera Cabriolet': 83240, '911 Carrera 4 Cabriolet': 89240},
                2007: {'911 Carrera': 77240, '911 Carrera 4': 83240, '911 Turbo': 131840, '911 Carrera Cabriolet': 84240, '911 Carrera 4 Cabriolet': 90240},
                2008: {'911 Carrera': 78600, '911 Carrera 4': 84600, '911 Turbo': 132600, '911 Carrera Cabriolet': 85600, '911 Carrera 4 Cabriolet': 91600},
                2009: {'911 Carrera': 79800, '911 Carrera 4': 85800, '911 Turbo': 133800, '911 Carrera Cabriolet': 86800, '911 Carrera 4 Cabriolet': 92800, '911 GT3': 115000},
                2010: {'911 Carrera': 81000, '911 Carrera 4': 87000, '911 Turbo': 135000, '911 Carrera Cabriolet': 88000, '911 Carrera 4 Cabriolet': 94000, '911 GT3': 116000},
                2011: {'911 Carrera': 82200, '911 Carrera 4': 88200, '911 Turbo': 136200, '911 Carrera Cabriolet': 89200, '911 Carrera 4 Cabriolet': 95200, '911 GT3': 117000},
                2012: {'911 Carrera': 84300, '911 Carrera S': 97400, '911 Carrera 4': 91400, '911 Carrera 4S': 104500, '911 Turbo': 148300, '911 Turbo S': 173200},
                2013: {'911 Carrera': 85195, '911 Carrera S': 98295, '911 Carrera 4': 92295, '911 Carrera 4S': 105395, '911 Turbo': 149195, '911 Turbo S': 174095},
                2014: {'911 Carrera': 85995, '911 Carrera S': 99095, '911 Carrera 4': 93095, '911 Carrera 4S': 106195, '911 Turbo': 149995, '911 Turbo S': 174895, '911 GT3': 130395},
                2015: {'911 Carrera': 86795, '911 Carrera S': 99895, '911 Carrera 4': 93895, '911 Carrera 4S': 106995, '911 Turbo': 150795, '911 Turbo S': 175695, '911 GT3': 131195},
                2016: {'911 Carrera': 89400, '911 Carrera S': 102100, '911 Carrera 4': 96500, '911 Carrera 4S': 109200, '911 Turbo': 159200, '911 Turbo S': 182050, '911 GT3': 143600, '911 GT3 RS': 175900},
                2017: {'911 Carrera': 90200, '911 Carrera S': 102900, '911 Carrera 4': 97300, '911 Carrera 4S': 110000, '911 Turbo': 160000, '911 Turbo S': 182850, '911 GT3': 144400, '911 GT3 RS': 176700},
                2018: {'911 Carrera': 91000, '911 Carrera S': 103700, '911 Carrera 4': 98100, '911 Carrera 4S': 110800, '911 Turbo': 160800, '911 Turbo S': 183650, '911 GT3': 145200, '911 GT3 RS': 177500},
                2019: {
                    '911 Carrera': 91800, '911 Carrera S': 104500, '911 Carrera 4': 98900, '911 Carrera 4S': 111600, 
                    '911 Turbo': 161600, '911 Turbo S': 184450, '911 GT3': 146000, '911 GT3 RS': 178300,
                    '911 Speedster': 274500
                },
                2020: {
                    '911 Carrera': 92600, '911 Carrera S': 105300, '911 Carrera 4': 99700, '911 Carrera 4S': 112400,
                    '911 Turbo': 170800, '911 Turbo S': 204850, '911 GT3': 143600, '911 GT2 RS': 293200
                },
                2021: {
                    '911 Carrera': 99200, '911 Carrera S': 113300, '911 Carrera 4': 106300, '911 Carrera 4S': 120400,
                    '911 Turbo': 172800, '911 Turbo S': 206850, '911 GT3': 161100, '911 GT3 Touring': 161100
                },
                2022: {
                    '911 Carrera': 101200, '911 Carrera S': 115300, '911 Carrera 4': 108300, '911 Carrera 4S': 122400,
                    '911 Turbo': 174800, '911 Turbo S': 208850, '911 GT3': 163100, '911 GT3 Touring': 163100,
                    '911 Carrera GTS': 131300, '911 Carrera 4 GTS': 138400
                },
                2023: {
                    '911 Carrera': 106100, '911 Carrera S': 120200, '911 Carrera 4': 113200, '911 Carrera 4S': 127300,
                    '911 Turbo': 179700, '911 Turbo S': 213700, '911 GT3': 169700, '911 GT3 Touring': 169700,
                    '911 Carrera GTS': 138600, '911 Carrera 4 GTS': 145700, '911 GT3 RS': 225250
                },
                2024: {
                    '911 Carrera': 108300, '911 Carrera S': 122400, '911 Carrera 4': 115400, '911 Carrera 4S': 129500,
                    '911 Turbo': 181900, '911 Turbo S': 215900, '911 GT3': 171900, '911 GT3 Touring': 171900,
                    '911 Carrera GTS': 140800, '911 Carrera 4 GTS': 147900, '911 GT3 RS': 227450
                },
                2025: {
                    '911 Carrera': 110500, '911 Carrera S': 124600, '911 Carrera 4': 117600, '911 Carrera 4S': 131700,
                    '911 Turbo': 184100, '911 Turbo S': 218100, '911 GT3': 174100, '911 GT3 Touring': 174100,
                    '911 Carrera GTS': 143000, '911 Carrera 4 GTS': 150100, '911 GT3 RS': 229650
                }
            }
        },
        'Cayenne': {
            'production_years': (2003, 2025),
            'trims_by_year': {
                2003: {'Cayenne': 53900, 'Cayenne S': 65400, 'Cayenne Turbo': 89800},
                2004: {'Cayenne': 54200, 'Cayenne S': 65700, 'Cayenne Turbo': 90100},
                2005: {'Cayenne': 54500, 'Cayenne S': 66000, 'Cayenne Turbo': 90400},
                2006: {'Cayenne': 54800, 'Cayenne S': 66300, 'Cayenne Turbo': 90700},
                2007: {'Cayenne': 55100, 'Cayenne S': 66600, 'Cayenne Turbo': 91000, 'Cayenne Turbo S': 103800},
                2008: {'Cayenne': 55900, 'Cayenne S': 67400, 'Cayenne Turbo': 91800, 'Cayenne Turbo S': 104600, 'Cayenne GTS': 75900},
                2009: {'Cayenne': 56700, 'Cayenne S': 68200, 'Cayenne Turbo': 92600, 'Cayenne Turbo S': 105400, 'Cayenne GTS': 76700},
                2010: {'Cayenne': 47000, 'Cayenne S': 60600, 'Cayenne Turbo': 108000, 'Cayenne Turbo S': 120000, 'Cayenne GTS': 66200},
                2011: {'Cayenne': 47300, 'Cayenne S': 60900, 'Cayenne Turbo': 108300, 'Cayenne Turbo S': 120300, 'Cayenne GTS': 66500},
                2012: {'Cayenne': 47600, 'Cayenne S': 61200, 'Cayenne Turbo': 108600, 'Cayenne Turbo S': 120600, 'Cayenne GTS': 66800},
                2013: {'Cayenne': 48495, 'Cayenne S': 62095, 'Cayenne Turbo': 109495, 'Cayenne Turbo S': 121495, 'Cayenne GTS': 67695},
                2014: {'Cayenne': 49295, 'Cayenne S': 62895, 'Cayenne Turbo': 110295, 'Cayenne Turbo S': 122295, 'Cayenne GTS': 68495, 'Cayenne S E-Hybrid': 76100},
                2015: {'Cayenne': 50095, 'Cayenne S': 63695, 'Cayenne Turbo': 111095, 'Cayenne Turbo S': 123095, 'Cayenne GTS': 69295, 'Cayenne S E-Hybrid': 76900},
                2016: {'Cayenne': 50895, 'Cayenne S': 64495, 'Cayenne Turbo': 111895, 'Cayenne Turbo S': 123895, 'Cayenne GTS': 70095, 'Cayenne S E-Hybrid': 77700},
                2017: {'Cayenne': 51695, 'Cayenne S': 65295, 'Cayenne Turbo': 112695, 'Cayenne Turbo S': 124695, 'Cayenne GTS': 70895, 'Cayenne S E-Hybrid': 78500},
                2018: {
                    'Cayenne': 65700, 'Cayenne S': 83600, 'Cayenne Turbo': 124600, 'Cayenne E-Hybrid': 80900
                },
                2019: {
                    'Cayenne': 66800, 'Cayenne S': 84700, 'Cayenne Turbo': 125700, 'Cayenne E-Hybrid': 81900,
                    'Cayenne Coupe': 75300, 'Cayenne S Coupe': 91300, 'Cayenne Turbo Coupe': 130100
                },
                2020: {
                    'Cayenne': 67000, 'Cayenne S': 84900, 'Cayenne Turbo': 125900, 'Cayenne E-Hybrid': 82100,
                    'Cayenne Coupe': 75500, 'Cayenne S Coupe': 91500, 'Cayenne Turbo Coupe': 130300,
                    'Cayenne GTS': 107300, 'Cayenne GTS Coupe': 109600
                },
                2021: {
                    'Cayenne': 68000, 'Cayenne S': 85900, 'Cayenne Turbo': 126900, 'Cayenne E-Hybrid': 83100,
                    'Cayenne Coupe': 76500, 'Cayenne S Coupe': 92500, 'Cayenne Turbo Coupe': 131300,
                    'Cayenne GTS': 108300, 'Cayenne GTS Coupe': 110600
                },
                2022: {
                    'Cayenne': 69400, 'Cayenne S': 87300, 'Cayenne Turbo': 128300, 'Cayenne E-Hybrid': 84500,
                    'Cayenne Coupe': 77900, 'Cayenne S Coupe': 93900, 'Cayenne Turbo Coupe': 132700,
                    'Cayenne GTS': 109700, 'Cayenne GTS Coupe': 112000, 'Cayenne Turbo GT': 180300
                },
                2023: {
                    'Cayenne': 71800, 'Cayenne S': 89700, 'Cayenne Turbo': 130700, 'Cayenne E-Hybrid': 86900,
                    'Cayenne Coupe': 80300, 'Cayenne S Coupe': 96300, 'Cayenne Turbo Coupe': 135100,
                    'Cayenne GTS': 112100, 'Cayenne GTS Coupe': 114400, 'Cayenne Turbo GT': 182700
                },
                2024: {
                    'Cayenne': 73400, 'Cayenne S': 91300, 'Cayenne Turbo': 132300, 'Cayenne E-Hybrid': 88500,
                    'Cayenne Coupe': 81900, 'Cayenne S Coupe': 97900, 'Cayenne Turbo Coupe': 136700,
                    'Cayenne GTS': 113700, 'Cayenne GTS Coupe': 116000, 'Cayenne Turbo GT': 184300
                },
                2025: {
                    'Cayenne': 75000, 'Cayenne S': 92900, 'Cayenne Turbo': 133900, 'Cayenne E-Hybrid': 90100,
                    'Cayenne Coupe': 83500, 'Cayenne S Coupe': 99500, 'Cayenne Turbo Coupe': 138300,
                    'Cayenne GTS': 115300, 'Cayenne GTS Coupe': 117600, 'Cayenne Turbo GT': 185900
                }
            }
        },
        'Macan': {
            'production_years': (2014, 2025),
            'trims_by_year': {
                2014: {'Macan S': 49900, 'Macan Turbo': 72300},
                2015: {'Macan': 47500, 'Macan S': 50900, 'Macan Turbo': 73200},
                2016: {'Macan': 48050, 'Macan S': 51450, 'Macan Turbo': 73750, 'Macan GTS': 67200},
                2017: {'Macan': 48550, 'Macan S': 51950, 'Macan Turbo': 74250, 'Macan GTS': 67700},
                2018: {'Macan': 49050, 'Macan S': 52450, 'Macan Turbo': 74750, 'Macan GTS': 68200},
                2019: {
                    'Macan': 50800, 'Macan S': 54250, 'Macan Turbo': 76550, 'Macan GTS': 70000
                },
                2020: {
                    'Macan': 51800, 'Macan S': 55250, 'Macan Turbo': 77550, 'Macan GTS': 71000
                },
                2021: {
                    'Macan': 52800, 'Macan S': 56250, 'Macan Turbo': 78550, 'Macan GTS': 72000
                },
                2022: {
                    'Macan': 54000, 'Macan S': 57450, 'Macan Turbo': 79750, 'Macan GTS': 73200
                },
                2023: {
                    'Macan': 55800, 'Macan S': 59250, 'Macan Turbo': 81550, 'Macan GTS': 75000
                },
                2024: {
                    'Macan': 57100, 'Macan S': 60550, 'Macan Turbo': 82850, 'Macan GTS': 76300,
                    'Macan 4': 59300
                },
                2025: {
                    'Macan': 58400, 'Macan S': 61850, 'Macan Turbo': 84150, 'Macan GTS': 77600,
                    'Macan 4': 60600, 'Macan 4S': 67000
                }
            }
        },
        'Panamera': {
            'production_years': (2010, 2025),
            'trims_by_year': {
                2010: {'Panamera S': 89800, 'Panamera 4S': 93800, 'Panamera Turbo': 132600},
                2011: {'Panamera': 75375, 'Panamera S': 90175, 'Panamera 4S': 94175, 'Panamera Turbo': 132975},
                2012: {'Panamera': 76075, 'Panamera S': 90875, 'Panamera 4S': 94875, 'Panamera Turbo': 133675, 'Panamera S E-Hybrid': 95000},
                2013: {'Panamera': 76970, 'Panamera S': 91770, 'Panamera 4S': 95770, 'Panamera Turbo': 134570, 'Panamera S E-Hybrid': 95895, 'Panamera GTS': 114200},
                2014: {'Panamera': 77770, 'Panamera S': 92570, 'Panamera 4S': 96570, 'Panamera Turbo': 135370, 'Panamera S E-Hybrid': 96695, 'Panamera GTS': 115000, 'Panamera Turbo S': 177200},
                2015: {'Panamera': 78570, 'Panamera S': 93370, 'Panamera 4S': 97370, 'Panamera Turbo': 136170, 'Panamera S E-Hybrid': 97495, 'Panamera GTS': 115800, 'Panamera Turbo S': 178000},
                2016: {'Panamera': 79370, 'Panamera S': 94170, 'Panamera 4S': 98170, 'Panamera Turbo': 136970, 'Panamera S E-Hybrid': 98295, 'Panamera GTS': 116600, 'Panamera Turbo S': 178800},
                2017: {
                    'Panamera': 85000, 'Panamera 4': 88200, 'Panamera 4S': 102200, 'Panamera Turbo': 147950,
                    'Panamera 4 E-Hybrid': 99600
                },
                2018: {
                    'Panamera': 86200, 'Panamera 4': 89400, 'Panamera 4S': 103400, 'Panamera Turbo': 149150,
                    'Panamera 4 E-Hybrid': 100800, 'Panamera GTS': 127900, 'Panamera Turbo S E-Hybrid': 184400
                },
                2019: {
                    'Panamera': 87200, 'Panamera 4': 90400, 'Panamera 4S': 104400, 'Panamera Turbo': 150150,
                    'Panamera 4 E-Hybrid': 101800, 'Panamera GTS': 128900, 'Panamera Turbo S E-Hybrid': 185400
                },
                2020: {
                    'Panamera': 87200, 'Panamera 4': 90400, 'Panamera 4S': 104400, 'Panamera Turbo': 150150,
                    'Panamera 4 E-Hybrid': 101800, 'Panamera GTS': 128900, 'Panamera Turbo S E-Hybrid': 185400
                },
                2021: {
                    'Panamera': 88400, 'Panamera 4': 91600, 'Panamera 4S': 105600, 'Panamera Turbo': 151350,
                    'Panamera 4 E-Hybrid': 103000, 'Panamera GTS': 130100, 'Panamera Turbo S E-Hybrid': 186600
                },
                2022: {
                    'Panamera': 90200, 'Panamera 4': 93400, 'Panamera 4S': 107400, 'Panamera Turbo': 153150,
                    'Panamera 4 E-Hybrid': 104800, 'Panamera GTS': 131900, 'Panamera Turbo S E-Hybrid': 188400
                },
                2023: {
                    'Panamera': 93300, 'Panamera 4': 96500, 'Panamera 4S': 110500, 'Panamera Turbo': 156250,
                    'Panamera 4 E-Hybrid': 107900, 'Panamera GTS': 135000, 'Panamera Turbo S E-Hybrid': 191500
                },
                2024: {
                    'Panamera': 95300, 'Panamera 4': 98500, 'Panamera 4S': 112500, 'Panamera Turbo': 158250,
                    'Panamera 4 E-Hybrid': 109900, 'Panamera GTS': 137000, 'Panamera Turbo S E-Hybrid': 193500
                },
                2025: {
                    'Panamera': 97300, 'Panamera 4': 100500, 'Panamera 4S': 114500, 'Panamera Turbo': 160250,
                    'Panamera 4 E-Hybrid': 111900, 'Panamera GTS': 139000, 'Panamera Turbo S E-Hybrid': 195500
                }
            }
        },
        'Boxster': {
            'production_years': (2000, 2016),
            'trims_by_year': {
                2000: {'Boxster': 39980, 'Boxster S': 49930},
                2001: {'Boxster': 40280, 'Boxster S': 50230},
                2002: {'Boxster': 40580, 'Boxster S': 50530},
                2003: {'Boxster': 40880, 'Boxster S': 50830},
                2004: {'Boxster': 41180, 'Boxster S': 51130},
                2005: {'Boxster': 43540, 'Boxster S': 53490},
                2006: {'Boxster': 43840, 'Boxster S': 53790},
                2007: {'Boxster': 44140, 'Boxster S': 54090},
                2008: {'Boxster': 46600, 'Boxster S': 56550},
                2009: {'Boxster': 47000, 'Boxster S': 56950, 'Boxster Spyder': 60900},
                2010: {'Boxster': 47400, 'Boxster S': 57350, 'Boxster Spyder': 61300},
                2011: {'Boxster': 47800, 'Boxster S': 57750, 'Boxster Spyder': 61700},
                2012: {'Boxster': 49500, 'Boxster S': 60900},
                2013: {'Boxster': 50395, 'Boxster S': 61795},
                2014: {'Boxster': 51195, 'Boxster S': 62595, 'Boxster GTS': 73500},
                2015: {'Boxster': 51995, 'Boxster S': 63395, 'Boxster GTS': 74300},
                2016: {'Boxster': 52795, 'Boxster S': 64195, 'Boxster GTS': 75100, 'Boxster Spyder': 84900}
            }
        },
        'Cayman': {
            'production_years': (2006, 2016),
            'trims_by_year': {
                2006: {'Cayman S': 58900},
                2007: {'Cayman': 49400, 'Cayman S': 59200},
                2008: {'Cayman': 49900, 'Cayman S': 59700},
                2009: {'Cayman': 50400, 'Cayman S': 60200},
                2010: {'Cayman': 50800, 'Cayman S': 60600},
                2011: {'Cayman': 51200, 'Cayman S': 61000},
                2012: {'Cayman': 52600, 'Cayman S': 62400, 'Cayman R': 66300},
                2013: {'Cayman': 53495, 'Cayman S': 63295},
                2014: {'Cayman': 54295, 'Cayman S': 64095, 'Cayman GTS': 75200},
                2015: {'Cayman': 55095, 'Cayman S': 64895, 'Cayman GTS': 76000, 'Cayman GT4': 84600},
                2016: {'Cayman': 55895, 'Cayman S': 65695, 'Cayman GTS': 76800, 'Cayman GT4': 85400}
            }
        },
        '718': {
            'production_years': (2017, 2025),
            'trims_by_year': {
                2017: {
                    '718 Boxster': 57050, '718 Boxster S': 68400, '718 Cayman': 55400, '718 Cayman S': 66800
                },
                2018: {
                    '718 Boxster': 57850, '718 Boxster S': 69200, '718 Cayman': 56200, '718 Cayman S': 67600,
                    '718 Boxster GTS': 80850, '718 Cayman GTS': 79800
                },
                2019: {
                    '718 Boxster': 58650, '718 Boxster S': 70000, '718 Cayman': 57000, '718 Cayman S': 68400,
                    '718 Boxster GTS': 81650, '718 Cayman GTS': 80600, '718 Cayman GT4': 100200, '718 Spyder': 97400
                },
                2020: {
                    '718 Boxster': 59650, '718 Boxster S': 71000, '718 Cayman': 58000, '718 Cayman S': 69400,
                    '718 Boxster GTS': 82650, '718 Cayman GTS': 81600, '718 Cayman GT4': 101200, '718 Spyder': 98400
                },
                2021: {
                    '718 Boxster': 60650, '718 Boxster S': 72000, '718 Cayman': 59000, '718 Cayman S': 70400,
                    '718 Boxster GTS 4.0': 87200, '718 Cayman GTS 4.0': 87200, '718 Cayman GT4': 102200, '718 Spyder': 99400
                },
                2022: {
                    '718 Boxster': 61850, '718 Boxster S': 73200, '718 Cayman': 60200, '718 Cayman S': 71600,
                    '718 Boxster GTS 4.0': 88400, '718 Cayman GTS 4.0': 88400, '718 Cayman GT4': 103400, '718 Spyder': 100600
                },
                2023: {
                    '718 Boxster': 64250, '718 Boxster S': 75600, '718 Cayman': 62600, '718 Cayman S': 74000,
                    '718 Boxster GTS 4.0': 90800, '718 Cayman GTS 4.0': 90800, '718 Cayman GT4': 105800, '718 Spyder': 103000
                },
                2024: {
                    '718 Boxster': 65650, '718 Boxster S': 77000, '718 Cayman': 64000, '718 Cayman S': 75400,
                    '718 Boxster GTS 4.0': 92200, '718 Cayman GTS 4.0': 92200, '718 Cayman GT4': 107200, '718 Spyder': 104400,
                    '718 Cayman Style Edition': 68300
                },
                2025: {
                    '718 Boxster': 67050, '718 Boxster S': 78400, '718 Cayman': 65400, '718 Cayman S': 76800,
                    '718 Boxster GTS 4.0': 93600, '718 Cayman GTS 4.0': 93600, '718 Cayman GT4': 108600, '718 Spyder': 105800,
                    '718 Cayman Style Edition': 69700
                }
            }
        },
        'Taycan': {
            'production_years': (2020, 2025),
            'trims_by_year': {
                2020: {
                    'Taycan 4S': 103800, 'Taycan Turbo': 150900, 'Taycan Turbo S': 185000
                },
                2021: {
                    'Taycan': 79900, 'Taycan 4S': 104400, 'Taycan Turbo': 151400, 'Taycan Turbo S': 185500,
                    'Taycan Cross Turismo': 90900, 'Taycan 4S Cross Turismo': 105100, 'Taycan Turbo Cross Turismo': 151100, 'Taycan Turbo S Cross Turismo': 186400
                },
                2022: {
                    'Taycan': 82700, 'Taycan 4S': 107200, 'Taycan Turbo': 154200, 'Taycan Turbo S': 188300,
                    'Taycan Cross Turismo': 93700, 'Taycan 4S Cross Turismo': 107900, 'Taycan Turbo Cross Turismo': 153900, 'Taycan Turbo S Cross Turismo': 189200,
                    'Taycan GTS': 131400, 'Taycan GTS Sport Turismo': 134500
                },
                2023: {
                    'Taycan': 86050, 'Taycan 4S': 110550, 'Taycan Turbo': 157550, 'Taycan Turbo S': 191650,
                    'Taycan Cross Turismo': 97050, 'Taycan 4S Cross Turismo': 111250, 'Taycan Turbo Cross Turismo': 157250, 'Taycan Turbo S Cross Turismo': 192550,
                    'Taycan GTS': 134750, 'Taycan GTS Sport Turismo': 137850
                },
                2024: {
                    'Taycan': 88200, 'Taycan 4S': 112700, 'Taycan Turbo': 159700, 'Taycan Turbo S': 193800,
                    'Taycan Cross Turismo': 99200, 'Taycan 4S Cross Turismo': 113400, 'Taycan Turbo Cross Turismo': 159400, 'Taycan Turbo S Cross Turismo': 194700,
                    'Taycan GTS': 137900, 'Taycan GTS Sport Turismo': 141000
                },
                2025: {
                    'Taycan': 90350, 'Taycan 4S': 114850, 'Taycan Turbo': 161850, 'Taycan Turbo S': 195950,
                    'Taycan Cross Turismo': 101350, 'Taycan 4S Cross Turismo': 115550, 'Taycan Turbo Cross Turismo': 161550, 'Taycan Turbo S Cross Turismo': 196850,
                    'Taycan GTS': 140050, 'Taycan GTS Sport Turismo': 143150
                }
            }
        }
    }
}

# Helper functions for accessing the database
def get_manufacturers_p():
    """Get all manufacturers starting with 'P'"""
    return list(MANUFACTURERS_P.keys())

def get_models_for_make_p(make):
    """Get all models for a specific make starting with 'P'"""
    return list(MANUFACTURERS_P.get(make, {}).keys())

def get_production_years_p(make, model):
    """Get production years for a specific make/model starting with 'P'"""
    model_data = MANUFACTURERS_P.get(make, {}).get(model, {})
    return model_data.get('production_years', (2000, 2025))

def get_trims_for_year_p(make, model, year):
    """Get available trims and prices for a specific year"""
    model_data = MANUFACTURERS_P.get(make, {}).get(model, {})
    trims_by_year = model_data.get('trims_by_year', {})
    
    # Return exact year if available
    if year in trims_by_year:
        return trims_by_year[year]
    
    # Find closest year if exact year not available
    available_years = sorted(trims_by_year.keys())
    if not available_years:
        return {}
    
    # Find closest year within production range
    production_start, production_end = get_production_years_p(make, model)
    if year < production_start:
        return trims_by_year.get(production_start, {})
    elif year > production_end:
        return trims_by_year.get(production_end, {})
    else:
        # Find closest available year
        closest_year = min(available_years, key=lambda x: abs(x - year))
        return trims_by_year.get(closest_year, {})

def is_model_available_in_year_p(make, model, year):
    """Check if a model was available in a specific year"""
    start_year, end_year = get_production_years_p(make, model)
    return start_year <= year <= end_year

def get_base_price_p(make, model, year):
    """Get the base (lowest) price for a model in a specific year"""
    trims = get_trims_for_year_p(make, model, year)
    return min(trims.values()) if trims else 0

def get_trim_price_p(make, model, trim, year):
    """Get price for a specific trim in a specific year"""
    trims = get_trims_for_year_p(make, model, year)
    return trims.get(trim, 0)

# Example usage and validation
if __name__ == "__main__":
    # Test the database
    print("Manufacturers starting with 'P':", get_manufacturers_p())
    print("\nPorsche models:", get_models_for_make_p('Porsche'))
    print("\n911 production years:", get_production_years_p('Porsche', '911'))
    print("\n2023 911 trims:", get_trims_for_year_p('Porsche', '911', 2023))
    print("\n2023 911 base price:", get_base_price_p('Porsche', '911', 2023))
    print("\nIs Cayenne available in 2010?", is_model_available_in_year_p('Porsche', 'Cayenne', 2010))
    print("Is Taycan available in 2015?", is_model_available_in_year_p('Porsche', 'Taycan', 2015))