SELECT usnationals2016.id,2x2.best,3x3.best,333bld.best,fmc.best,333ft.best,333mlt.best,333oh.best,4x4.best,444bld.best,5x5.best,555bld.best,6x6.best,7x7.best,clock.best,mega.best,pyra.best,skewb.best,sq1.best,usnationals2016.birthdate FROM
usnationals2016
LEFT JOIN (SELECT * FROM RanksAverage WHERE eventId="222") 2x2 ON usnationals2016.wcaid = 2x2.personId
LEFT JOIN (SELECT * FROM RanksAverage WHERE eventId="333") 3x3 ON usnationals2016.wcaid = 3x3.personId
LEFT JOIN (SELECT * FROM RanksSingle WHERE eventId="333bf") 333bld ON usnationals2016.wcaid = 333bld.personId
LEFT JOIN (SELECT * FROM RanksSingle WHERE eventId="333fm") fmc ON usnationals2016.wcaid = fmc.personId
LEFT JOIN (SELECT * FROM RanksAverage WHERE eventId="333ft") 333ft ON usnationals2016.wcaid = 333ft.personId
LEFT JOIN (SELECT * FROM RanksSingle WHERE eventId="333mbf") 333mlt ON usnationals2016.wcaid = 333mlt.personId
LEFT JOIN (SELECT * FROM RanksAverage WHERE eventId="333oh") 333oh ON usnationals2016.wcaid = 333oh.personId
LEFT JOIN (SELECT * FROM RanksAverage WHERE eventId="444") 4x4 ON usnationals2016.wcaid = 4x4.personId
LEFT JOIN (SELECT * FROM RanksSingle WHERE eventId="444bf") 444bld ON usnationals2016.wcaid = 444bld.personId
LEFT JOIN (SELECT * FROM RanksAverage WHERE eventId="555") 5x5 ON usnationals2016.wcaid = 5x5.personId
LEFT JOIN (SELECT * FROM RanksSingle WHERE eventId="555bf") 555bld ON usnationals2016.wcaid = 555bld.personId
LEFT JOIN (SELECT * FROM RanksAverage WHERE eventId="666") 6x6 ON usnationals2016.wcaid = 6x6.personId
LEFT JOIN (SELECT * FROM RanksAverage WHERE eventId="777") 7x7 ON usnationals2016.wcaid = 7x7.personId
LEFT JOIN (SELECT * FROM RanksAverage WHERE eventId="clock") clock ON usnationals2016.wcaid = clock.personId
LEFT JOIN (SELECT * FROM RanksAverage WHERE eventId="minx") mega ON usnationals2016.wcaid = mega.personId
LEFT JOIN (SELECT * FROM RanksAverage WHERE eventId="pyram") pyra ON usnationals2016.wcaid = pyra.personId
LEFT JOIN (SELECT * FROM RanksAverage WHERE eventId="skewb") skewb ON usnationals2016.wcaid = skewb.personId
LEFT JOIN (SELECT * FROM RanksAverage WHERE eventId="sq1") sq1 ON usnationals2016.wcaid = sq1.personId
ORDER BY 1 ASC

