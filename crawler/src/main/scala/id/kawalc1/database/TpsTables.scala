package id.kawalc1.database

import java.sql.Timestamp

import enumeratum.values.SlickValueEnumSupport
import id.kawalc1
import id.kawalc1._
import slick.dbio.Effect
import slick.jdbc.PostgresProfile.api._
import slick.lifted.Tag
import slick.sql.FixedSqlAction

object TpsTables extends SlickValueEnumSupport {
  val profile = slick.jdbc.PostgresProfile

  class Kelurahan(tag: Tag) extends Table[KelurahanId](tag, "kelurahan") {
    def idKel = column[Int]("idKel", O.PrimaryKey)
    def nama = column[String]("nama")

    override def * = (idKel, nama) <> (KelurahanId.tupled, KelurahanId.unapply)
  }

  val kelurahanQuery = TableQuery[Kelurahan]

  class Tps(tag: Tag) extends Table[SingleTps](tag, "tps") {

    def id = column[Int]("kelurahan")
    def nama = column[String]("nama")
    def tps = column[Int]("tps")
    def timestamp = column[Timestamp]("ts")
    def photo = column[String]("photo", O.PrimaryKey)
    def plano = column[Option[Short]]("plano")
    def formType = column[Option[Short]]("form_type")
    def halaman = column[Option[String]]("halaman")

    def common = (cakupan, pending, error, janggal)

    def cakupan = column[Option[Int]]("cakupan")
    def pending = column[Option[Int]]("pending")
    def error = column[Option[Int]]("error")
    def janggal = column[Option[Int]]("janggal")

    def presLembar2 = (pas1, pas2, sah, tSah)

    def pas1 = column[Option[Int]]("pas1")
    def pas2 = column[Option[Int]]("pas2")
    def sah = column[Option[Int]]("sah")
    def tSah = column[Option[Int]]("tSah")
    def partai = column[Option[String]]("partai")
    def partaiJum = column[Option[Int]]("partai_jum")
    def jum = column[Option[Int]]("jum")

    private def upackPresidential(sum: Option[Summary]) = {
      sum.flatMap {
        case p: PresidentialLembar2 =>
          Some(Some(p.pas1), Some(p.pas2), Some(p.sah), Some(p.tSah))
        case _ => None
      }
    }

    private def upackDpr(sum: Option[Summary]) = {
      sum match {
        case Some(x: Dpr) => Some(x)

        case _ => None
      }
    }

    override def * =
      (id, nama, tps, timestamp, photo, plano, formType, halaman, common, presLembar2, partai, partaiJum, jum).shaped <> ({

        case (id, nama, tps, timestamp, photo, plano, formType, halaman, common, presLembar2, partai, partaiJum, jum) =>
          val sum = formType match {
            case Some(FormType.PPWP.value) =>
              presLembar2._1 match {
                case Some(_) =>
                  Some((PresidentialLembar2.apply _).tupled(presLembar2._1.get, presLembar2._2.get, presLembar2._3.get, presLembar2._4.get))
                case None => None
              }
            case Some(FormType.DPR.value) =>
              partai.map(x => Dpr(x, partaiJum.get))
            case _ => None
          }
          SingleTps(
            nama,
            photo,
            id,
            tps,
            Verification(
              timestamp,
              plano.map(x => C1(Plano.withValueOpt(x), FormType.withValue(formType.get), halaman)),
              sum,
              (Common.apply _).tupled(common)))
      }, { v: SingleTps =>
        val plano = v.verification.c1.flatMap(_.plano.map(_.value))
        val formType = v.verification.c1.map(_.`type`.value)
        val halaman = v.verification.c1.flatMap(_.halaman)
        val maybePresidential = upackPresidential(v.verification.sum)
        val summaryFields = maybePresidential.getOrElse((None, None, None, None))
        val maybeDpr = upackDpr(v.verification.sum)
        val maybeJum = v.verification.sum match {
          case Some(SingleSum(x)) => Some(x)
          case _ => None
        }
        val partai = maybeDpr.map(_.partai)
        val partaiVotes = maybeDpr.map(_.votes)

        val common = v.verification.common

        Some(
          v.kelurahanId,
          v.nama,
          v.tpsId,
          v.verification.ts,
          v.photo,
          plano,
          formType,
          halaman,
          Common.unapply(common).get,
          summaryFields,
          partai,
          partaiVotes,
          maybeJum)
      })
  }

  val tpsQuery = TableQuery[Tps]

  def upsertTps(results: Seq[Seq[SingleTps]]): Seq[FixedSqlAction[Int, NoStream, Effect.Write]] = {
    results.flatten.map(tpsQuery.insertOrUpdate)
  }

}
