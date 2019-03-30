package id.kawalc1.database

import java.sql.Timestamp

import enumeratum.values.SlickValueEnumSupport
import id.kawalc1
import id.kawalc1.{
  C1,
  Dpr,
  FormType,
  KelurahanId,
  Plano,
  PresidentialLembar2,
  SingleTps,
  Summary,
  Verification
}
import slick.ast.ColumnOption.PrimaryKey
import slick.lifted.Tag
import slick.jdbc.SQLiteProfile.api._

object Tables extends SlickValueEnumSupport {
  val profile = slick.jdbc.SQLiteProfile

  class Kelurahan(tag: Tag) extends Table[KelurahanId](tag, "kelurahan") {
    def idKel = column[Int]("idKel", O.PrimaryKey)
    def nama  = column[String]("nama")

    override def * = (idKel, nama) <> (KelurahanId.tupled, KelurahanId.unapply)
  }

  val kelurahanQuery = TableQuery[Kelurahan]

  class Tps(tag: Tag) extends Table[SingleTps](tag, "tps") {
    implicit lazy val planoMapper    = mappedColumnTypeForValueEnum(Plano)
    implicit lazy val formTypeMapper = mappedColumnTypeForValueEnum(FormType)

    def id = column[Int]("kelurahan")

    def nama = column[String]("nama")

    def tps = column[Int]("tps")

    def timestamp = column[Timestamp]("ts")

    def photo = column[String]("photo", O.PrimaryKey)

    def plano = column[Option[Plano]]("plano")

    def formType = column[Option[FormType]]("form_type")

    def presLembar2 = (pas1, pas2, sah, tSah)

    def pas1 = column[Option[Int]]("pas1")

    def pas2 = column[Option[Int]]("pas2")

    def sah = column[Option[Int]]("sah")

    def tSah = column[Option[Int]]("tSah")

    def pkb = column[Option[Int]]("pkb")

    def ger = column[Option[Int]]("ger")

    def pdi = column[Option[Int]]("pdi")

    def gol = column[Option[Int]]("gol")

    def nas = column[Option[Int]]("nas")

    def gar = column[Option[Int]]("gar")

    def ber = column[Option[Int]]("ber")

    def sej = column[Option[Int]]("sej")

    def per = column[Option[Int]]("per")

    def ppp = column[Option[Int]]("ppp")

    def psi = column[Option[Int]]("psi")

    def pan = column[Option[Int]]("pan")

    def han = column[Option[Int]]("han")

    def dem = column[Option[Int]]("dem")

    def pa = column[Option[Int]]("pa")

    def ps = column[Option[Int]]("ps")

    def pda = column[Option[Int]]("pda")

    def pna = column[Option[Int]]("pna")

    def pbb = column[Option[Int]]("pbb")

    def pkp = column[Option[Int]]("pkp")

    def parties =
      (pkb,
       ger,
       pdi,
       gol,
       nas,
       gar,
       ber,
       sej,
       per,
       ppp,
       psi,
       pan,
       han,
       dem,
       pa,
       ps,
       pda,
       pna,
       pbb,
       pkp)

    private def upackPresidential(sum: Option[Summary]) = {
      sum.flatMap {
        case p: PresidentialLembar2 =>
          Some(Some(p.pas1), Some(p.pas2), Some(p.sah), Some(p.tSah))
        case _ => None
      }
    }

    private def upackDpr(sum: Option[Summary]) = {
      val emptyResults = kawalc1.Parties.map(_ => Option.empty[Int])
      val dprResults = sum match {
        case Some(x: Dpr) =>
          val resultmap = kawalc1.Parties.zip(emptyResults).toMap
          resultmap.map {
            case (index: String, _: Option[Int]) => index -> x.votes.get(index).flatten
          }.values

        case _ => emptyResults
      }
      dprResults.toSeq
    }

    override def * =
      (id, nama, tps, timestamp, photo, plano, formType, presLembar2, parties).shaped <> ({
        case (id, nama, tps, timestamp, photo, plano, formType, presLembar2, parties) =>
          val bla = parties
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
            case Some(FormType.DPR) =>
              val partyColumns = kawalc1.Parties
                .zip(parties.productIterator.toSeq)
                .toMap
                .mapValues(_.asInstanceOf[Option[Int]])
              Some(Dpr(votes = partyColumns))
            case _ => None
          }
          SingleTps(nama,
                    photo,
                    id,
                    tps,
                    Verification(timestamp, plano.map(C1(_, formType.get)), sum))
      }, { v: SingleTps =>
        val plano                       = v.verification.c1.map(_.plano)
        val formType                    = v.verification.c1.map(_.`type`)
        val maybeTyple                  = upackPresidential(v.verification.sum)
        val summaryFields               = maybeTyple.getOrElse((None, None, None, None))
        val dprFields: Seq[Option[Int]] = upackDpr(v.verification.sum)
        val tupled = dprFields match {
          case Seq(pkb,
                   ger,
                   pdi,
                   gol,
                   nas,
                   gar,
                   ber,
                   sej,
                   per,
                   ppp,
                   psi,
                   pan,
                   han,
                   dem,
                   pa,
                   ps,
                   pda,
                   pna,
                   pbb,
                   pkp) =>
            (pkb,
             ger,
             pdi,
             gol,
             nas,
             gar,
             ber,
             sej,
             per,
             ppp,
             psi,
             pan,
             han,
             dem,
             pa,
             ps,
             pda,
             pna,
             pbb,
             pkp)

        }

        Some(v.kelurahanId,
             v.nama,
             v.tpsId,
             v.verification.ts,
             v.photo,
             plano,
             formType,
             summaryFields,
             tupled)
      })
  }

  val tpsQuery = TableQuery[Tps]

}
