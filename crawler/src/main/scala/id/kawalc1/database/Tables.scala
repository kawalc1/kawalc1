package id.kawalc1.database

import java.sql.Timestamp

import enumeratum.values.SlickValueEnumSupport
import id.kawalc1.{C1, FormType, Plano, PresidentialLembar2, SingleTps, Summary, Verification}
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

    def presLembar2 = (pas1, pas2, sah, tSah)

    def pas1 = column[Option[Int]]("pas1")

    def pas2 = column[Option[Int]]("pas2")

    def sah = column[Option[Int]]("sah")

    def tSah = column[Option[Int]]("tSah")

    private def unpackSummary(sum: Option[Summary]) = {
      val bla = sum.map {
        case p: PresidentialLembar2 =>
          Some(Some(p.pas1), Some(p.pas2), Some(p.sah), Some(p.tSah))
        case _ => None
      }
      println(s"$bla")
      bla.flatten

    }

    override def * =
      (id, tps, timestamp, photo, plano, formType, presLembar2).shaped <> ({
        case (id, tps, timestamp, photo, plano, formType, presLembar2) =>
          val sum = formType match {
            case Some(FormType.PPWP) =>
              presLembar2._1 match {
                case Some(_) =>
                  Some(
                    (PresidentialLembar2.apply _).tupled(presLembar2._1.get,
                                                         presLembar2._2.get,
                                                         presLembar2._3.get,
                                                         presLembar2._4.get))
                case None => None
              }
            case _ => None
          }
          SingleTps(photo, id, tps, Verification(timestamp, plano.map(C1(_, formType.get)), sum))
      }, { v: SingleTps =>
        val plano         = v.verification.c1.map(_.plano)
        val formType      = v.verification.c1.map(_.`type`)
        val maybeTyple    = unpackSummary(v.verification.sum)
        val summaryFields = maybeTyple.getOrElse((None, None, None, None))

        Some(v.kelurahanId, v.tpsId, v.verification.ts, v.photo, plano, formType, summaryFields)
      })
  }

  val tpsQuery = TableQuery[Tps]

}
