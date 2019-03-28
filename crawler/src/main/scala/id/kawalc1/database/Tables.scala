package id.kawalc1.database

import java.sql.Timestamp

import enumeratum.values.SlickValueEnumSupport
import id.kawalc1.{C1, FormType, Plano, SingleTps, Verification}
import slick.ast.ColumnOption.PrimaryKey
import slick.lifted.Tag
import slick.jdbc.SQLiteProfile.api._

object Tables extends SlickValueEnumSupport {
  val profile = slick.jdbc.SQLiteProfile

  class Tps(tag: Tag) extends Table[SingleTps](tag, "tps") {
    implicit lazy val planoMapper    = mappedColumnTypeForValueEnum(Plano)
    implicit lazy val formTypeMapper = mappedColumnTypeForValueEnum(FormType)

    def id = column[Int]("kelurahan")

    def tps = column[Int]("tps")

    def timestamp = column[Timestamp]("ts", PrimaryKey)

    def photo = column[String]("photo")

    def plano = column[Option[Plano]]("plano")

    def formType = column[Option[FormType]]("form_type")

    override def * =
      (id, tps, timestamp, photo, plano, formType).shaped <> ({
        case (id, tps, timestamp, photo, plano, formType) =>
          SingleTps(photo, id, tps, Verification(timestamp, plano.map(C1(_, formType.get)), None))
      }, { v: SingleTps =>
        val plano    = v.verification.c1.map(_.plano)
        val formType = v.verification.c1.map(_.`type`)
        Some(v.kelurahanId, v.tpsId, v.verification.ts, v.photo, plano, formType)
      })
  }

  val tpsQuery = TableQuery[Tps]

}
