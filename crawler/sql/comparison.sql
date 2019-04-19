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
ORDER by 'pas1-pas2-match' DESC