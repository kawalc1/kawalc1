WITH duplicates AS (SELECT hash,
                           COUNT(*) AS total
                    FROM detections
                    WHERE LENGTH(hash) > 10
                    GROUP BY hash
                    HAVING COUNT(*) > 1),
     doubles AS (SELECT d.kelurahan AS kel1,
                        d.tps       AS tps1,
                        t.total_completed_tps,
                        CASE
                            WHEN d.roi IS NULL THEN t.uploaded_photo_url
                            ELSE REPLACE(d.roi, 'digit-area', 'lokasi')
                            END     AS photo1,
                        d.hash,
                        t.update_ts
                 FROM detections AS d
                          INNER JOIN "tps-photo" AS t ON d.photo = t.uploaded_photo_id
                          INNER JOIN duplicates ON duplicates.hash = d.hash
                 WHERE duplicates.total = 2),
     result AS (SELECT d1.kel1,
                       d1.tps1,
                       d2.kel1   AS kel2,
                       d2.tps1   AS tps2,
                       d1.photo1,
                       d2.photo1 AS photo2,
                       d1.hash,
                       d1.update_ts
                FROM doubles d1
                         INNER JOIN doubles d2 ON d1.hash = d2.hash
                WHERE d1.photo1 <> d2.photo1
                  AND (d1.kel1 <> d2.kel1 OR d1.tps1 <> d2.tps1)),
     ultimate AS (SELECT DISTINCT ON (r.hash) r.kel1,
                                              r.tps1,
                                              r.kel2,
                                              r.tps2,
                                              r.photo1,
                                              r.photo2,
                                              r.hash,
                                              r.update_ts
                  FROM result r)
select *
from ultimate u
where u.kel1 = u.kel2
order by update_ts DESC;
