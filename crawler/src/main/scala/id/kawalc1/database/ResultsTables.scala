package id.kawalc1.database

import enumeratum.values.SlickValueEnumSupport
import id.kawalc1
import id.kawalc1._
import id.kawalc1.database.CustomPostgresProfile.api._
import id.kawalc1.services.BlockingSupport
import slick.dbio.Effect
import slick.lifted.Tag
import slick.sql.FixedSqlAction

case class Terbalik(kelurahan: Int,
                    tps: Int,
                    pas1: Int,
                    pas2: Int,
                    jumlah: Int,
                    tidakSah: Int,
                    hal2Photo: String,
                    php: Int,
                    hal1Photo: String)

case class AlignResult(id: Long,
                       tps: Int,
                       response: String,
                       responseCode: Int,
                       photo: String,
                       photoSize: Int,
                       alignQuality: Double,
                       config: String,
                       featureAlgorithm: String,
                       alignedUrl: Option[String],
                       extracted: Option[Boolean],
                       hash: Option[String])

case class ExtractResult(id: Long,
                         tps: Int,
                         photo: String,
                         response: String,
                         responseCode: Int,
                         digitArea: String,
                         config: String,
                         tpsArea: String)

case class PresidentialResult(id: Long,
                              tps: Int,
                              photo: String,
                              response: String,
                              responseCode: Int,
                              pas1: Int,
                              pas2: Int,
                              jumlahCalon: Int,
                              calonConfidence: Double,
                              jumlahSah: Int,
                              tidakSah: Int,
                              jumlahSeluruh: Int,
                              jumlahConfidence: Double)

case class DetectionResult(kelurahan: Long,
                           tps: Int,
                           photo: String,
                           response_code: Int,
                           config: Option[String],
                           pas1: Option[Int],
                           pas2: Option[Int],
                           pas3: Option[Int],
                           jumlah: Option[Int],
                           tidak_sah: Option[Int],
                           confidence: Option[Double],
                           confidence_tidak_sah: Option[Double],
                           hash: Option[String],
                           similarity: Option[Double],
                           aligned: Option[String],
                           roi: Option[String],
                           response: String)

object ResultsTables extends SlickValueEnumSupport with BlockingSupport {
  val profile = id.kawalc1.database.CustomPostgresProfile

  class DetectionResults(tag: Tag) extends Table[DetectionResult](tag, "detections") {
    def kelurahan            = column[Long]("kelurahan")
    def tps                  = column[Int]("tps")
    def photo                = column[String]("photo", O.PrimaryKey)
    def response_code        = column[Int]("response_code")
    def config               = column[Option[String]]("config")
    def pas1                 = column[Option[Int]]("pas1")
    def pas2                 = column[Option[Int]]("pas2")
    def pas3                 = column[Option[Int]]("pas3")
    def jumlah               = column[Option[Int]]("jumlah")
    def tidak_sah            = column[Option[Int]]("tidak_sah")
    def confidence           = column[Option[Double]]("confidence")
    def confidence_tidak_sah = column[Option[Double]]("confidence_tidak_sah")
    def hash                 = column[Option[String]]("hash")
    def similarity           = column[Option[Double]]("similarity")
    def aligned              = column[Option[String]]("aligned", O.SqlType("TEXT"))
    def roi                  = column[Option[String]]("roi", O.SqlType("TEXT"))
    def response             = column[String]("response", O.SqlType("TEXT"))

    override def * =
      (kelurahan,
       tps,
       photo,
       response_code,
       config,
       pas1,
       pas2,
       pas3,
       jumlah,
       tidak_sah,
       confidence,
       confidence_tidak_sah,
       hash,
       similarity,
       aligned,
       roi,
       response) <> (DetectionResult.tupled, DetectionResult.unapply)
  }

  val detectionsQuery = TableQuery[DetectionResults]

  class AlignResults(tag: Tag) extends Table[AlignResult](tag, "align_results") {
    def id               = column[Long]("kelurahan")
    def tps              = column[Int]("tps")
    def response         = column[String]("response", O.SqlType("TEXT"))
    def responseCode     = column[Int]("response_code")
    def photo            = column[String]("photo", O.PrimaryKey)
    def photoSize        = column[Int]("photo_size")
    def alignQuality     = column[Double]("align_quality")
    def config           = column[String]("config")
    def featureAlgorithm = column[String]("feature_algorithm")
    def alignedUrl       = column[Option[String]]("aligned_url")
    def extracted        = column[Option[Boolean]]("extracted")
    def hash             = column[Option[String]]("hash")

    override def * =
      (id, tps, response, responseCode, photo, photoSize, alignQuality, config, featureAlgorithm, alignedUrl, extracted, hash) <> (AlignResult.tupled, AlignResult.unapply)
  }

  val alignResultsQuery = TableQuery[AlignResults]

  class ProblemResults(tag: Tag) extends Table[Problem](tag, "problems") {
    def kelId         = column[Int]("kelurahan")
    def kelName       = column[String]("kelurahan_name")
    def tpsNo         = column[Int]("tps")
    def url           = column[String]("url", O.PrimaryKey)
    def reason        = column[String]("reason")
    def ts            = column[Int]("ts")
    def response_code = column[Option[Int]]("response_code")

    def pk = primaryKey("primary_pk", (url, reason))

    override def * = (kelId, kelName, tpsNo, url, reason, ts, response_code) <> (Problem.tupled, Problem.unapply)
  }

  val problemsQuery = TableQuery[ProblemResults]

  class ProblemsReported(tag: Tag) extends Table[ProblemReported](tag, "problems_reported") {
    def kelId   = column[Int]("kelurahan")
    def kelName = column[String]("kelurahan_name")
    def tpsNo   = column[Int]("tps")
    def url     = column[String]("url")
    def reason  = column[String]("reason")

    def pk = primaryKey("primary_pk", (url, reason))

    override def * =
      (kelId, kelName, tpsNo, url, reason) <>
        (ProblemReported.tupled, ProblemReported.unapply)
  }

  val problemsReportedQuery = TableQuery[ProblemsReported]

  class FormsProcessed(tag: Tag) extends Table[FormProcessed](tag, "forms_processed") {
    def kelId = column[Int]("kelurahan")
    def tpsNo = column[Int]("tps")
    def url   = column[String]("url", O.PrimaryKey)

    override def * =
      (kelId, tpsNo, url) <>
        (FormProcessed.tupled, FormProcessed.unapply)
  }

  val formsProcessedQuery = TableQuery[FormsProcessed]

  class ExtractResults(tag: Tag) extends Table[ExtractResult](tag, "extract_results") {
    def id           = column[Long]("kelurahan")
    def tps          = column[Int]("tps")
    def photo        = column[String]("photo", O.PrimaryKey)
    def response     = column[String]("response", O.SqlType("TEXT"))
    def responseCode = column[Int]("response_code")

    def digitArea = column[String]("digit_area")
    def config    = column[String]("config")
    def tpsArea   = column[String]("tps_area")

    override def * =
      (id, tps, photo, response, responseCode, digitArea, config, tpsArea) <> (ExtractResult.tupled, ExtractResult.unapply)
  }

  val extractResultsQuery = TableQuery[ExtractResults]

  class Terbaliks(tag: Tag) extends Table[Terbalik](tag, "terbalik") {
    def kelurahan  = column[Int]("kelurahan")
    def tps        = column[Int]("tps")
    def pas1       = column[Int]("bot-pas1")
    def pas2       = column[Int]("bot-pas2")
    def jumlah     = column[Int]("bot-jumlah")
    def tidakSah   = column[Int]("bot-tidak-sah")
    def hal2Photo  = column[String]("hal2photo")
    def php        = column[Int]("bot-php")
    def hal1Photo  = column[String]("hal1photo")
    override def * = (kelurahan, tps, pas1, pas2, jumlah, tidakSah, hal2Photo, php, hal1Photo) <> (Terbalik.tupled, Terbalik.unapply)
  }

  val terbaliksQuery = TableQuery[Terbaliks]

  class PresidentialResults(tag: Tag) extends Table[PresidentialResult](tag, "presidential_results") {
    def id    = column[Long]("kelurahan")
    def tps   = column[Int]("tps")
    def photo = column[String]("photo", O.PrimaryKey)

    def response     = column[String]("response")
    def responseCode = column[Int]("response_code")

    def pas1            = column[Int]("pas1")
    def pas2            = column[Int]("pas2")
    def jumlahCalon     = column[Int]("jumlah_calon")
    def calonConfidence = column[Double]("calon_conf")

    def jumlahSah        = column[Int]("jumlah_sah")
    def tidakSah         = column[Int]("tidak_sah")
    def jumlahSeluruh    = column[Int]("jumlah_seluruh")
    def jumlahConfidence = column[Double]("jumlah_conf")

    override def * =
      (id,
       tps,
       photo,
       response,
       responseCode,
       pas1,
       pas2,
       jumlahCalon,
       calonConfidence,
       jumlahSah,
       tidakSah,
       jumlahSeluruh,
       jumlahConfidence) <>
        (PresidentialResult.tupled, PresidentialResult.unapply)
  }

  val presidentialResultsQuery = TableQuery[PresidentialResults]

  def singleTpsQuery(url: String) = {
    TpsTables.tpsPhotoQuery.filter(_.uploadedPhotoUrl === url)
  }

  def alignErrorQuery = {
    val joined = for {
      (a, b) <- TpsTables.tpsPhotoQuery join alignResultsQuery on (_.uploadedPhotoUrl === _.photo)
    } yield (a, b)
    joined.filter(_._2.responseCode === 500).map(_._1)
    //    joined.filter { case (a, b: AlignResults) => b.responseCode === 200 }.map(_._1).filter(_.formType === FormType.PPWP.value)
  }

  def extractErrorQuery = {
    val joined = for {
      (a, b) <- alignResultsQuery join extractResultsQuery on (_.photo === _.photo)
    } yield (a, b)
    joined
      .filter(_._2.responseCode === 500)
      .map(_._1)
  }

  def tpsToAlignQuery(plano: Plano, halaman: String = "2") = {
    val joined = for {
      (a: TpsTables.TpsPhotoTable, b: Rep[Option[AlignResults]]) <- TpsTables.tpsPhotoQuery joinLeft alignResultsQuery on (_.uploadedPhotoUrl === _.photo)
    } yield (a, b)
    joined
      .filter { case (a, b) => b.isEmpty }
      .map(_._1)
    //      .filter(x => x.formType === FormType.PPWP.value && x.halaman === halaman)
  }

  def tpsToExtractQuery = {
    val joined = for {
      (a, b) <- alignResultsQuery.filter(_.alignQuality > 1.0) joinLeft extractResultsQuery on (_.photo === _.photo)
    } yield (a, b)
    joined
      .filter { case (a, b) => b.isEmpty }
      .map(_._1)
  }

  def problemsToReportQuery = {
    val joined = for {
      (a, b) <- problemsQuery joinLeft problemsReportedQuery on (_.url === _.url)
    } yield (a, b)
    joined
      .filter { case (a, b) => b.isEmpty }
      .map(_._1)
  }

  def tpsToDetectQuery(offset: Int): Query[TpsTables.TpsPhotoTable, kawalc1.SingleTpsPhotoDao, Seq] = {
    val joined = for {
      (a: TpsTables.TpsPhotoTable, b: Rep[Option[DetectionResults]]) <- (TpsTables.tpsPhotoQuery joinLeft detectionsQuery on (_.uploadedPhotoId === _.photo))
        .sortBy(_._1.kelurahanId)
    } yield (a, b)
    joined
      .filter { case (a, b) => b.isEmpty }
      .map(_._1)
  }

  def tpsToRoiQuery = {
    val joined = for {
      (a, b) <- TpsTables.tpsPhotoQuery join detectionsQuery on (_.uploadedPhotoUrl === _.photo)
    } yield (a, b)
    joined
      .map(_._1)
      .filter(x => x.formType === FormType.PPWP.value && x.halaman === "2" && x.plano === Plano.NO.value)
  }

  def upsertAlign(results: Seq[AlignResult]): Seq[FixedSqlAction[Option[Int], NoStream, Effect.Write]] = {
    Seq(alignResultsQuery.insertOrUpdateAll(results))
  }

  def upsertExtract(results: Seq[ExtractResult]): Seq[FixedSqlAction[Option[Int], NoStream, Effect.Write]] = {
    Seq(extractResultsQuery.insertOrUpdateAll(results))
  }

  def upsertPresidential(results: Seq[PresidentialResult]): Seq[FixedSqlAction[Option[Int], NoStream, Effect.Write]] = {
    Seq(presidentialResultsQuery.insertOrUpdateAll(results))
  }

  private val sedotDatabase = Database.forConfig("sedotDatabase")
  def upsertDetections(results: Seq[DetectionResult]): Seq[FixedSqlAction[Option[Int], NoStream, Effect.Write]] = {
    val detectionsInsert = detectionsQuery.insertOrUpdateAll(results)
    //    sedotDatabase.run(detectionsInsert).futureValue
    Seq(detectionsInsert)
  }
}
