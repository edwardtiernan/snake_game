
files = ['trialfile01.inp', 'trialfile02.inp', 'trialfile03.inp', 'trialfile04.inp', 'trialfile05.inp',
            'trialfile06.inp', 'trialfile07.inp',
            'trialfile08.inp', 'trialfile09.inp', 'trialfile10.inp', 'trialfile11.inp', 'trialfile12.inp',
            'trialfile13.inp', 'trialfile14.inp',
            'trialfile15.inp', 'trialfile16.inp', 'trialfile17.inp', 'trialfile18.inp', 'trialfile19.inp',
            'trialfile20.inp', 'trialfile21.inp',
            'trialfile22.inp', 'trialfile23.inp', 'trialfile24.inp', 'trialfile25.inp', 'trialfile26.inp',
            'trialfile27.inp', 'trialfile28.inp',
            'trialfile29.inp', 'trialfile30.inp', 'trialfile31.inp', 'trialfile32.inp', 'trialfile33.inp',
            'trialfile34.inp', 'trialfile35.inp',
            'trialfile36.inp', 'trialfile37.inp', 'trialfile38.inp', 'trialfile39.inp', 'trialfile40.inp',
            'trialfile41.inp', 'trialfile42.inp',
            'trialfile43.inp', 'trialfile44.inp', 'trialfile45.inp', 'trialfile46.inp', 'trialfile47.inp',
            'trialfile48.inp', 'trialfile49.inp',
            'trialfile50.inp', 'trialfile51.inp', 'trialfile52.inp', 'trialfile53.inp', 'trialfile54.inp',
            'trialfile55.inp', 'trialfile56.inp',
            'trialfile57.inp', 'trialfile58.inp', 'trialfile59.inp', 'trialfile60.inp', 'trialfile61.inp',
            'trialfile62.inp', 'trialfile63.inp',
            'trialfile64.inp', 'trialfile65.inp', 'trialfile66.inp', 'trialfile67.inp', 'trialfile68.inp',
            'trialfile69.inp', 'trialfile70.inp',
            'trialfile71.inp', 'trialfile72.inp', 'trialfile73.inp', 'trialfile74.inp', 'trialfile75.inp',
            'trialfile76.inp', 'trialfile77.inp',
            'trialfile78.inp', 'trialfile79.inp', 'trialfile80.inp', 'trialfile81.inp', 'trialfile82.inp',
            'trialfile83.inp', 'trialfile84.inp',
            'trialfile85.inp', 'trialfile86.inp', 'trialfile87.inp', 'trialfile88.inp', 'trialfile89.inp',
            'trialfile90.inp', 'trialfile91.inp',
            'trialfile92.inp', 'trialfile93.inp', 'trialfile94.inp', 'trialfile95.inp', 'trialfile96.inp',
            'trialfile97.inp', 'trialfile98.inp',
            'trialfile99.inp', 'trialfile100.inp']
Qfiles = ['trialfile101.inp', 'trialfile102.inp', 'trialfile103.inp', 'trialfile104.inp', 'trialfile105.inp',
            'trialfile106.inp', 'trialfile107.inp',
            'trialfile108.inp', 'trialfile109.inp', 'trialfile110.inp', 'trialfile111.inp', 'trialfile112.inp',
            'trialfile113.inp', 'trialfile114.inp',
            'trialfile115.inp', 'trialfile116.inp', 'trialfile117.inp', 'trialfile118.inp', 'trialfile119.inp',
            'trialfile120.inp', 'trialfile121.inp',
            'trialfile122.inp', 'trialfile123.inp', 'trialfile124.inp', 'trialfile125.inp', 'trialfile126.inp',
            'trialfile127.inp', 'trialfile128.inp',
            'trialfile129.inp', 'trialfile130.inp', 'trialfile131.inp', 'trialfile132.inp', 'trialfile133.inp',
            'trialfile134.inp', 'trialfile135.inp',
            'trialfile136.inp', 'trialfile137.inp', 'trialfile138.inp', 'trialfile139.inp', 'trialfile140.inp',
            'trialfile141.inp', 'trialfile142.inp',
            'trialfile143.inp', 'trialfile144.inp', 'trialfile145.inp', 'trialfile146.inp', 'trialfile147.inp',
            'trialfile148.inp', 'trialfile149.inp',
            'trialfile150.inp', 'trialfile151.inp', 'trialfile152.inp', 'trialfile153.inp', 'trialfile154.inp',
            'trialfile155.inp', 'trialfile156.inp',
            'trialfile157.inp', 'trialfile158.inp', 'trialfile159.inp', 'trialfile160.inp', 'trialfile161.inp',
            'trialfile162.inp', 'trialfile163.inp',
            'trialfile164.inp', 'trialfile165.inp', 'trialfile166.inp', 'trialfile167.inp', 'trialfile168.inp',
            'trialfile169.inp', 'trialfile170.inp',
            'trialfile171.inp', 'trialfile172.inp', 'trialfile173.inp', 'trialfile174.inp', 'trialfile175.inp',
            'trialfile176.inp', 'trialfile177.inp',
            'trialfile178.inp', 'trialfile179.inp', 'trialfile180.inp', 'trialfile181.inp', 'trialfile182.inp',
            'trialfile183.inp', 'trialfile184.inp',
            'trialfile185.inp', 'trialfile186.inp', 'trialfile187.inp', 'trialfile188.inp', 'trialfile189.inp',
            'trialfile190.inp', 'trialfile191.inp',
            'trialfile192.inp', 'trialfile193.inp', 'trialfile194.inp', 'trialfile195.inp', 'trialfile196.inp',
            'trialfile197.inp', 'trialfile198.inp',
            'trialfile199.inp', 'trialfile200.inp']
Unionsets = files + Qfiles

global settingsdict, geneticdict

# settingsdict = {'inputfilename': "1001_Brentwood_1D_Existing_Monitoring_rev1.inp", 'root': "BW1", 'constraintfilename': 'Parameter_ranges.txt',
#                 'filelist': files, 'Qfilelist': Qfiles, 'Unionsetlist': Unionsets, 'distancefilename':
#                     "001_Brentwood_1D_Existing_Monitoring_rev1.inp", 'observationdatafile': "BW1flow_120208-141231_rev1.dat", 'weights':
#                      [1/4, 1/4, 1/4, 1/4], 'multiprocessors': 4}

settingsdict = {'inputfilename': "Example1.inp", 'root': "18", 'constraintfilename': 'Parameter_ranges.txt',
                'filelist': files, 'Qfilelist': Qfiles, 'Unionsetlist': Unionsets, 'distancefilename':
                    "Example1_ModelFinal.inp", 'observationdatafile': "trial_observation.dat", 'weights':
                    [1/4, 1/4, 1/4, 1/4], 'multiprocessors': 8}

geneticdict = {'initial_mutation': 0.5, 'population': 100, 'nsga_mutation': 0.1, 'crossover_bias': 0.5,
               'generations': 3}