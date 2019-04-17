package id.kawalc1.services

import akka.NotUsed
import akka.stream.Materializer
import akka.stream.scaladsl.{ Source => StreamSource }
import id.kawalc1
import id.kawalc1.clients.{ Extraction, JsonSupport, KawalC1Client, KawalPemiluClient, Response }
import id.kawalc1.database.ResultsTables.{ AlignResults, ExtractResults }
import id.kawalc1.database.TpsTables.{ Kelurahan => KelurahanTable, Tps }
import id.kawalc1.database._
import id.kawalc1.{ FormType, Kelurahan, KelurahanId, ProbabilitiesResponse, SingleTps }
import org.json4s.native.Serialization
import slick.dbio.Effect
import slick.jdbc.SQLiteProfile
import slick.jdbc.SQLiteProfile.api._
import slick.sql.FixedSqlAction

import scala.concurrent.duration.{ FiniteDuration, _ }
import scala.concurrent.{ ExecutionContext, Future }

case class AlignedPicture(url: String, imageSize: Int)

class PhotoProcessor(client: KawalC1Client, kawalPemiluClient: KawalPemiluClient)(implicit val ex: ExecutionContext, mat: Materializer)
  extends JsonSupport
  with BlockingSupport {
  override def duration: FiniteDuration = 1.hour

  val ImageSize = 1280
  val FeatureAlgorithm = "akaze"
  val url = "http://lh3.googleusercontent.com/HZ6AJF6YYqA2M5MXxH99XedoaE1Rk3-IelJEsnosBVPLdMb73X0w7T5_mWvExCsIZlI-cud3kSU9Lk7c700"

  private def transform[A, B](
    sourceDb: SQLiteProfile.backend.Database,
    targetDb: SQLiteProfile.backend.Database,
    query: Seq[A],
    process: Seq[A] => Future[Seq[B]],
    insert: Seq[B] => Seq[FixedSqlAction[Int, NoStream, Effect.Write]]) = {
    for {
      processed <- process(query)
      inserted <- targetDb.run(DBIO.sequence(insert(processed)))
    } yield inserted

  }

  private def batchTransform[A, B, C <: Table[A]](
    sourceDb: SQLiteProfile.backend.Database,
    targetDb: SQLiteProfile.backend.Database,
    query: Query[C, C#TableElementType, Seq],
    process: Seq[A] => Future[Seq[B]],
    insert: Seq[B] => Seq[FixedSqlAction[Int, NoStream, Effect.Write]],
    offset: Long,
    batchSize: Long) = {
    var numberOfItems = 0
    var start: Long = offset
    do {
      val nextBatch = query.drop(start).take(batchSize)
      val items = sourceDb.run(nextBatch.result).futureValue
      numberOfItems = items.length
      val inserted = transform(sourceDb, targetDb, items, process, insert).futureValue
      logger.info(s"Inserted batch $start - ${start + offset}. # of items: ${inserted.length}")
      start += batchSize
    } while (numberOfItems > 0)
    start + numberOfItems
  }

  def align(sourceDb: SQLiteProfile.backend.Database, targetDb: SQLiteProfile.backend.Database, offset: Long, batchSize: Long): Long = {

    batchTransform[SingleTps, AlignResult, Tps](
      sourceDb,
      targetDb,
      TpsTables.tpsQuery.filter(_.formType === FormType.PPWP.value), //.filter(_.photo === url),
      alignPhoto,
      ResultsTables.upsertAlign,
      offset,
      batchSize)
  }

  def fetch(sourceDb: SQLiteProfile.backend.Database, targetDb: SQLiteProfile.backend.Database, offset: Long, batchSize: Long): Long = {

    batchTransform[KelurahanId, Seq[SingleTps], KelurahanTable](
      sourceDb,
      targetDb,
      TpsTables.kelurahanQuery,
      fetchTps,
      TpsTables.upsertTps,
      offset,
      batchSize)
  }

  def fetchTps(kelurahan: Seq[KelurahanId]) = {
    streamResults(kelurahan.map(_.idKel.toLong), getSingleLurah)
  }

  def getSingleLurah(number: Long) = {
    kawalPemiluClient
      .getKelurahan(number)
      .map {
        case Right(kel) => Kelurahan.toTps(kel)
        case Left(_) => Seq.empty
      }
  }

  def extract(sourceDb: SQLiteProfile.backend.Database, targetDb: SQLiteProfile.backend.Database, offset: Long, batchSize: Long): Long =
    batchTransform[AlignResult, ExtractResult, AlignResults](
      sourceDb,
      targetDb,
      ResultsTables.alignResultsQuery.filter(_.photo === url),
      extractNumbers,
      ResultsTables.upsertExtract,
      offset,
      batchSize)

  def processProbabilities(
    sourceDb: SQLiteProfile.backend.Database,
    targetDb: SQLiteProfile.backend.Database,
    offset: Long,
    batchSize: Long): Long =
    batchTransform[ExtractResult, PresidentialResult, ExtractResults](
      sourceDb,
      targetDb,
      ResultsTables.extractResultsQuery,
      processProbabilities,
      ResultsTables.upsertPresidential,
      offset,
      batchSize)

  def alignPhoto(tps: Seq[SingleTps]): Future[Seq[AlignResult]] = {
    streamResults(tps, alignSinglePhoto)
  }

  private def alignSinglePhoto(tps: SingleTps): Future[AlignResult] = {
    val photo: Array[String] = tps.photo.split("/")
    val photoUrl = photo(photo.length - 1)
    val formType = tps.verification.c1.get.`type`
    val formConfig = kawalc1.formTypeToConfig(formType)
    client.alignPhoto(tps.kelurahanId, tps.tpsId, photoUrl, ImageSize, formConfig, FeatureAlgorithm).map {
      case Right(t) =>
        t.transformedUrl match {
          case Some(trans) =>
            AlignResult(
              tps.kelurahanId,
              tps.tpsId,
              Serialization.write(t),
              200,
              tps.photo,
              ImageSize,
              t.similarity,
              formConfig,
              FeatureAlgorithm,
              Some(trans),
              None,
              Some(t.hash))
          case None =>
            AlignResult(
              tps.kelurahanId,
              tps.tpsId,
              Serialization.write(t),
              200,
              tps.photo,
              ImageSize,
              -1.0,
              formConfig,
              FeatureAlgorithm,
              None,
              None,
              Some(t.hash))
        }
      case Left(resp) =>
        AlignResult(
          tps.kelurahanId,
          tps.tpsId,
          resp.response,
          resp.code,
          tps.photo,
          ImageSize,
          -1.0,
          formConfig,
          FeatureAlgorithm,
          None,
          None,
          None)
    }
  }

  private def extractNumbers(results: Seq[AlignResult]): Future[Seq[ExtractResult]] = {
    Future
      .sequence(results.map { res: AlignResult =>
        val alignedLastSegment = res.alignedUrl.get.split("/")
        val alignedFileName = alignedLastSegment(alignedLastSegment.length - 1)
        for {
          extracted <- client.extractNumbers(res.id, res.tps, alignedFileName, res.config)
        } yield {
          extracted match {
            case Right(e: Extraction) =>
              ExtractResult(res.id, res.tps, res.photo, Serialization.write(e), 200, e.digitArea, res.config, "")
            case Left(resp) =>
              ExtractResult(res.id, res.tps, res.photo, resp.response, resp.code, "", res.config, "")
          }
        }
      })
  }

  private def streamResults[A: Manifest, B](toProcess: Seq[A], func: A => Future[B]): Future[Seq[B]] = {
    val Parallelism = 10
    val futures: StreamSource[B, NotUsed] =
      StreamSource[A](toProcess.toList)
        .mapAsync(Parallelism)(func)

    futures.runFold(Seq.empty[B])(_ :+ _)
  }

  private def processProbabilities(results: Seq[ExtractResult]): Future[Seq[PresidentialResult]] = {
    streamResults(results, procesExtractResults)
  }

  private def procesExtractResults(res: ExtractResult) = {
    for {
      extracted <- {
        val extraction = Serialization.read[Extraction](res.response)
        client.processProbabilities(res.id, res.tps, extraction.numbers, res.config)
      }
    } yield {
      extracted match {
        case Right(p: ProbabilitiesResponse) =>
          val first = p.probabilityMatrix.head.head
          val second = p.probabilityMatrix.tail.head.head

          val pas1 = first.numbers.filter(_.shortName == "jokowi").head.number
          val pas2 = first.numbers.filter(_.shortName == "prabowo").head.number
          val jumlahCalon = first.numbers.filter(_.shortName == "jumlah").head.number
          val calonConfidence = first.confidence

          val jumlah = second.numbers.filter(_.shortName == "jumlah").head.number
          val tidakSah = second.numbers.filter(_.shortName == "tidakSah").head.number
          val jumlahSeluruh = second.numbers.filter(_.shortName == "jumlahSeluruh").head.number
          val jumlahConfidence = second.confidence

          PresidentialResult(
            id = res.id,
            tps = res.tps,
            photo = res.photo,
            response = Serialization.write(p),
            responseCode = 200,
            pas1 = pas1,
            pas2 = pas2,
            jumlahCalon = jumlahCalon,
            calonConfidence = calonConfidence,
            jumlahSah = jumlah,
            tidakSah = tidakSah,
            jumlahSeluruh = jumlahSeluruh,
            jumlahConfidence = jumlahConfidence)
        case Left(resp) =>
          PresidentialResult(
            id = res.id,
            tps = res.tps,
            photo = res.photo,
            response = resp.response,
            responseCode = resp.code.intValue(),
            pas1 = -1,
            pas2 = -1,
            jumlahCalon = -1,
            calonConfidence = -1.0,
            jumlahSah = -1,
            tidakSah = -1,
            jumlahSeluruh = -1,
            jumlahConfidence = -1)
      }
    }
  }
}
