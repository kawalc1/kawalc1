SELECT distinct p.kelurahan, p.tps,
--t.photo,
                p.pas1 AS "bot-pas1", t.pas1,
                p.pas2 AS "bot-pas2", t.pas2,
                p.jumlah AS "bot-jumlah", t.pas1 + t.pas2 AS "jumlah",
                -1 as "jumlah-sah",
                p.tidak_sah AS "bot-tidak-sah", "tSah" as "tidak-sah",
                t.pas1 = p.pas1 AND t.pas2 = p.pas2 as "pasmatch",
                "tSah" = p.tidak_sah AS "tidak-sah-match",
                p.hash,
                p.aligned,
                p.roi,
                p.confidence,
                p.confidence_tidak_sah,
                p.photo,
                p.config,
                p.php_jumlah AS "bot-php",
                t.jum AS "php",
                p.php_jumlah = t.jum as "php-match",
                t.error AS error,
                similarity
FROM detections AS p
         INNER JOIN tps AS t ON p.photo = t.photo
         inner join (SELECT a.*
                     FROM duplicates a
                              JOIN (SELECT duplicates.hash, COUNT(*)
                                    FROM duplicates inner join tps on duplicates.photo = tps.photo
                                    GROUP BY duplicates.hash
                                    HAVING count(*) > 1 ) b
                                   ON a.hash = b.hash
--where config ISNULL
                     ORDER BY a.hash ) d on d.photo = p.photo
where length(p.hash) > 10
ORDER BY hash desc