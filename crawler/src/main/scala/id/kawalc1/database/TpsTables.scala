package id.kawalc1.database

import com.typesafe.scalalogging.LazyLogging
import enumeratum.values.SlickValueEnumSupport
import id.kawalc1._
import id.kawalc1.database.CustomPostgresProfile.api._
import id.kawalc1.services.BlockingSupport
import slick.collection.heterogeneous.HNil
import slick.dbio.Effect
import slick.lifted.Tag
import slick.sql.FixedSqlAction

import java.sql.Timestamp
import scala.concurrent.ExecutionContext

object TpsTables extends SlickValueEnumSupport with BlockingSupport with LazyLogging {
  val profile = id.kawalc1.database.CustomPostgresProfile

  class Kelurahan(tag: Tag) extends Table[KelurahanId](tag, "kelurahan") {
    def idKel = column[Long]("idkel", O.PrimaryKey)
    def nama  = column[String]("nama")

    override def * = (idKel, nama) <> (KelurahanId.tupled, KelurahanId.unapply)
  }

  val kelurahanQuery = TableQuery[Kelurahan]

  class TpsPhotoTable(tag: Tag) extends Table[SingleTpsPhotoDao](tag, "tps-photo") {
    def kelurahanId      = column[Long]("kelurahan_id")
    def tpsId            = column[Int]("tps_id")
    def name             = column[String]("name")
    def idLokasi         = column[String]("id_lokasi")
    def uid              = column[Option[String]]("uid")
    def updatedTs        = column[Timestamp]("update_ts")
    def uploadedPhotoId  = column[String]("uploaded_photo_id", O.PrimaryKey)
    def uploadedPhotoUrl = column[String]("uploaded_photo_url")

    def dpt  = column[Int]("dpt")
    def pas1 = column[Option[Int]]("pas1")
    def pas2 = column[Option[Int]]("pas2")
    def pas3 = column[Option[Int]]("pas3")

    def pas1Agg = column[Option[Int]]("pas1_agg")
    def pas2Agg = column[Option[Int]]("pas2_agg")
    def pas3Agg = column[Option[Int]]("pas3_agg")

    def anyPendingTps     = column[Option[String]]("any_pending_tps")
    def totalTps          = column[Int]("total_tps")
    def totalPendingTps   = column[Int]("total_pending_tps")
    def totalCompletedTps = column[Int]("total_completed_tps")
    def totalErrorTps     = column[Int]("total_error_tps")

    // We need to see if these can be determined
    def formType    = column[Option[Short]]("form_type")
    def plano       = column[Option[Short]]("plano")
    def halaman     = column[Option[String]]("halaman")
    def lastUpdated = column[Timestamp]("last_updated")

    override def * =
      (kelurahanId ::
        tpsId ::
        name ::
        idLokasi ::
        uid ::
        updatedTs ::
        uploadedPhotoId ::
        uploadedPhotoUrl ::
        dpt ::
        pas1 ::
        pas2 ::
        pas3 ::
        pas1Agg ::
        pas2Agg ::
        pas3Agg ::
        anyPendingTps ::
        totalTps ::
        totalPendingTps ::
        totalCompletedTps ::
        totalErrorTps ::
        formType ::
        plano ::
        halaman ::
        lastUpdated :: HNil).mapTo[SingleTpsPhotoDao]

  }

  val tpsPhotoQuery = TableQuery[TpsPhotoTable]

  class TpsTable(tag: Tag) extends Table[SingleTpsDao](tag, "tps") {
    def kelurahanId      = column[Long]("kelurahan_id")
    def tpsId            = column[Int]("tps_id")
    def name             = column[String]("name")
    def idLokasi         = column[String]("id_lokasi", O.PrimaryKey)
    def uid              = column[Option[String]]("uid")
    def updatedTs        = column[Timestamp]("update_ts")
    def uploadedPhotoId  = column[Option[String]]("uploaded_photo_id")
    def uploadedPhotoUrl = column[Option[String]]("uploaded_photo_url")

    def dpt  = column[Int]("dpt")
    def pas1 = column[Option[Int]]("pas1")
    def pas2 = column[Option[Int]]("pas2")
    def pas3 = column[Option[Int]]("pas3")

    def anyPendingTps     = column[Option[String]]("any_pending_tps")
    def totalTps          = column[Int]("total_tps")
    def totalPendingTps   = column[Int]("total_pending_tps")
    def totalCompletedTps = column[Int]("total_completed_tps")
    def totalErrorTps     = column[Int]("total_error_tps")
    def lastUpdated       = column[Timestamp]("last_updated")

    override def * =
      (kelurahanId,
       tpsId,
       name,
       idLokasi,
       uid,
       updatedTs,
       uploadedPhotoId,
       uploadedPhotoUrl,
       dpt,
       pas1,
       pas2,
       pas3,
       anyPendingTps,
       totalTps,
       totalPendingTps,
       totalCompletedTps,
       totalErrorTps,
       lastUpdated) <> (SingleTpsDao.tupled, SingleTpsDao.unapply)

  }
  val tpsQuery = TableQuery[TpsTable]

  class TpsOldDao(tag: Tag) extends Table[SingleOldTps](tag, "tps-old") {

    def id        = column[Int]("kelurahan")
    def nama      = column[String]("nama")
    def tps       = column[Int]("tps")
    def timestamp = column[Timestamp]("ts")
    def photo     = column[String]("photo", O.PrimaryKey)
    def plano     = column[Option[Short]]("plano")
    def formType  = column[Option[Short]]("form_type")
    def halaman   = column[Option[String]]("halaman")

    def common = (cakupan, pending, error, janggal)

    def cakupan = column[Option[Int]]("cakupan")
    def pending = column[Option[Int]]("pending")
    def error   = column[Option[Int]]("error")
    def janggal = column[Option[Int]]("janggal")

    def presLembar2 = (pas1, pas2, sah, tSah)

    def pas1      = column[Option[Int]]("pas1")
    def pas2      = column[Option[Int]]("pas2")
    def sah       = column[Option[Int]]("sah")
    def tSah      = column[Option[Int]]("tSah")
    def partai    = column[Option[String]]("partai")
    def partaiJum = column[Option[Int]]("partai_jum")
    def jum       = column[Option[Int]]("jum")

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
          SingleOldTps(
            nama,
            photo,
            None,
            id,
            tps,
            VerificationOld(timestamp,
                            plano.map(x => C1(Plano.withValueOpt(x), FormType.withValue(formType.get), halaman)),
                            sum,
                            (Common.apply _).tupled(common))
          )
      }, { v: SingleOldTps =>
        val plano             = v.verification.c1.flatMap(_.plano.map(_.value))
        val formType          = v.verification.c1.map(_.`type`.value)
        val halaman           = v.verification.c1.flatMap(_.halaman)
        val maybePresidential = upackPresidential(v.verification.sum)
        val summaryFields     = maybePresidential.getOrElse((None, None, None, None))
        val maybeDpr          = upackDpr(v.verification.sum)
        val maybeJum = v.verification.sum match {
          case Some(SingleSum(x)) => Some(x)
          case _                  => None
        }
        val partai      = maybeDpr.map(_.partai)
        val partaiVotes = maybeDpr.map(_.votes)

        val common = v.verification.common

        Some(v.kelurahanId,
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

  val tpsOldQuery = TableQuery[TpsOldDao]

  class TpsUnverified(tag: Tag) extends Table[SingleOldTps](tag, "tps_unverified") {

    def id        = column[Int]("kelurahan")
    def nama      = column[String]("nama")
    def tps       = column[Int]("tps")
    def timestamp = column[Timestamp]("ts")
    def photo     = column[String]("photo", O.PrimaryKey)
    def plano     = column[Option[Short]]("plano")
    def formType  = column[Option[Short]]("form_type")
    def halaman   = column[Option[String]]("halaman")

    def common = (cakupan, pending, error, janggal)

    def cakupan = column[Option[Int]]("cakupan")
    def pending = column[Option[Int]]("pending")
    def error   = column[Option[Int]]("error")
    def janggal = column[Option[Int]]("janggal")

    def presLembar2 = (pas1, pas2, sah, tSah)

    def pas1      = column[Option[Int]]("pas1")
    def pas2      = column[Option[Int]]("pas2")
    def sah       = column[Option[Int]]("sah")
    def tSah      = column[Option[Int]]("tsah")
    def partai    = column[Option[String]]("partai")
    def partaiJum = column[Option[Int]]("partai_jum")
    def jum       = column[Option[Int]]("jum")
    def imageId   = column[Option[String]]("image_id")

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
      (id, nama, tps, timestamp, photo, plano, formType, halaman, common, presLembar2, partai, partaiJum, jum, imageId).shaped <> ({

        case (id, nama, tps, timestamp, photo, plano, formType, halaman, common, presLembar2, partai, partaiJum, jum, imageId) =>
          val sum = formType match {
            case Some(FormType.PPWP.value) =>
              halaman match {
                case Some("1") =>
                  //                  println(s"jum $jum")
                  Some(SingleSum(jum.get))
                case Some("2") =>
                  Some((PresidentialLembar2.apply _).tupled(presLembar2._1.get, presLembar2._2.get, presLembar2._3.get, presLembar2._4.get))
              }
            case Some(FormType.DPR.value) =>
              partai.map(x => Dpr(x, partaiJum.get))
            case _ => None
          }
          SingleOldTps(
            nama,
            photo,
            imageId,
            id,
            tps,
            VerificationOld(timestamp,
                            plano.map(x => C1(Plano.withValueOpt(x), FormType.withValue(formType.get), halaman)),
                            sum,
                            (Common.apply _).tupled(common))
          )
      }, { v: SingleOldTps =>
        val plano             = v.verification.c1.flatMap(_.plano.map(_.value))
        val formType          = v.verification.c1.map(_.`type`.value)
        val halaman           = v.verification.c1.flatMap(_.halaman)
        val maybePresidential = upackPresidential(v.verification.sum)
        val summaryFields     = maybePresidential.getOrElse((None, None, None, None))
        val maybeDpr          = upackDpr(v.verification.sum)
        val maybeJum = v.verification.sum match {
          case Some(SingleSum(x)) => Some(x)
          case _                  => None
        }
        val partai      = maybeDpr.map(_.partai)
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
          maybeJum,
          v.imageId
        )
      })
  }

  val tpsUnverifiedQuery = TableQuery[TpsUnverified]

  private val sedotDatabase = Database.forConfig("sedotDatabase")

  def upsertTps(results: Seq[TpsBasedData])(implicit ex: ExecutionContext): Seq[FixedSqlAction[Option[Int], NoStream, Effect.Write]] = {
    val tpsData   = results.flatMap(_.plain)
    val tpsInsert = tpsQuery.insertOrUpdateAll(tpsData)

    val photosData = results.flatMap(_.withPhoto)
    println(s"PLAIN: ${tpsData.size}, PHOTOS: ${photosData.size}")
    val photosInsert = tpsPhotoQuery.insertOrUpdateAll(photosData)

    val uploaded = sedotDatabase.run(tpsInsert).futureValue
    logger.info(s"Uploaded ${tpsData.size} records into the sedot DB")

    Seq(tpsInsert, photosInsert)
  }

}
