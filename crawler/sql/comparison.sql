SELECT p.kelurahan, p.tps, p.pas1
AS 'bot-pas1', t.pas1, p.pas2
AS 'bot-pas2', t.pas2, p.jumlah_calon
AS 'bot-jumlah', t.pas1 + t.pas2, p.jumlah_sah,
t.pas1 = p.pas1 and t.pas2 = t.pas2 as 'pas1-pas2-match',
a.hash,
a.aligned_url
FROM presidential_results AS p
INNER JOIN tps AS t ON p.photo = t.photo
INNER JOIN align_results  AS a ON p.photo = a.photo
ORDER by 'pas1-pas2-match' DE


SELECT COUNT(*) FROM (select kelurahan, tps, REPLACE(photo,'http://lh3.googleusercontent.com/','') AS photo  FROM align_results AS a
WHERE config = 'digit_config_ppwp_scan_halaman_1_2019.json'
)

SELECT COUNT(*) FROM (
SELECT p.kelurahan, p.tps,
p.pas1  AS 'bot-pas1', t.pas1,
p.pas2  AS 'bot-pas2', t.pas2,
p.jumlah_calon  AS 'bot-jumlah', t.pas1 + t.pas2 AS 'jumlah',
p.jumlah_sah,
p.tidak_sah AS 'bot-tidak-sah', t.tSah as 'tidak-sah',
t.pas1 = p.pas1 AND t.pas2 = p.pas2 as 'pas-match',
t.tSah = p.tidak_sah 'tidak-sah-match',
a.hash,
a.aligned_url,
e.digit_area,
p.calon_conf,
p.jumlah_conf,
p.photo
FROM presidential_results AS p
INNER JOIN tps AS t ON p.photo = t.photo
INNER JOIN extract_results AS e ON e.photo = a.photo
INNER JOIN align_results  AS a ON p.photo = a.photo
WHERE `pas-match` = 0
AND p.calon_conf > 0.05
AND p.calon_conf <> 1
AND p.jumlah_calon <> 0
)