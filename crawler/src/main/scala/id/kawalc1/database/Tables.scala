package id.kawalc1.database

import java.sql.Timestamp
import java.time.Instant

import id.kawalc1.{SingleTps, Verification}
import slick.lifted.Tag
import slick.jdbc.H2Profile.api._

object Tables {

  class Tps(tag: Tag) extends Table[SingleTps](tag, "tps") {
    def id = column[Int]("kelurahan", O.PrimaryKey)

    def timestamp = column[Timestamp]("ts")

    def photo = column[String]("photo")

    override def * = (id, timestamp, photo).shaped <> ( {
      case (id, timestamp, photo) => SingleTps(photo, id, 1, Verification(timestamp, None, None))
    }, {
      v: SingleTps => Some(v.kelurahanId, v.verification.ts, v.photo)
    }
    )
  }

  val tpsQuery = TableQuery[Tps]

}
