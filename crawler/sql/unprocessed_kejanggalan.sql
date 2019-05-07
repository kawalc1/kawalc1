SELECT p.kelurahan, p.tps,
--t.photo,
       p.pas1  AS 'bot-pas1', t.pas1,
       p.pas2  AS 'bot-pas2', t.pas2,
       p.jumlah  AS 'bot-jumlah', t.pas1 + t.pas2 AS 'jumlah',
       -1 as 'jumlah-sah',
       p.tidak_sah AS 'bot-tidak-sah', t.tSah as 'tidak-sah',
       t.pas1 = p.pas1 AND t.pas2 = p.pas2 as 'pas-match',
       t.tSah = p.tidak_sah 'tidak-sah-match',
       p.hash,
       p.aligned,
       p.roi,
       p.confidence,
       p.confidence_tidak_sah,
       p.photo,
       p.config,
       p.php_jumlah AS 'bot-php',
       t.jum AS 'php',
       p.php_jumlah = t.jum as 'php-match',
       IFNULL(t.error,0) AS error,
       similarity,
       pr.url
FROM detections AS p
         INNER JOIN tps AS t ON p.photo = t.photo
         LEFT OUTER JOIN forms_processed pr on pr.url = p.photo
WHERE p.config = 'digit_config_ppwp_scan_halaman_2_2019.json'
  AND pr.url ISNULL
  AND p.confidence > 0.01
  AND (`pas-match` = 0 OR `tidak-sah-match` = 0)
  AND p.pas1 < 300 AND p.pas2 < 300 AND p.jumlah < 400 AND p.jumlah > 20