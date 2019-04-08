package id.kawalc1.services

import id.kawalc1
import id.kawalc1.clients.{Extraction, JsonSupport, KawalC1Client}
import id.kawalc1.database.{
  AlignResult,
  ExtractResult,
  PresidentialResult,
  ResultsTables,
  TpsTables
}
import id.kawalc1.{FormType, ProbabilitiesResponse, SingleTps}
import org.json4s.native.Serialization
import slick.dbio.Effect
import slick.jdbc.SQLiteProfile
import slick.jdbc.SQLiteProfile.api._
import slick.sql.{FixedSqlAction, FixedSqlStreamingAction}

import scala.concurrent.{ExecutionContext, Future}

case class AlignedPicture(url: String, imageSize: Int)

class PhotoProcessor(client: KawalC1Client)(implicit val ex: ExecutionContext) extends JsonSupport {

  val ImageSize = 1280

  private def transform[A, B](
      sourceDb: SQLiteProfile.backend.Database,
      targetDb: SQLiteProfile.backend.Database,
      query: FixedSqlStreamingAction[Seq[A], A, Effect.Read],
      process: Seq[A] => Future[Seq[Either[String, B]]],
      insert: Seq[B] => Seq[FixedSqlAction[Int, NoStream, Effect.Write]]) = {
    for {
      alignResults   <- sourceDb.run(query)
      extractResults <- process(alignResults)
      inserted <- {
        val toInsert = extractResults.flatMap {
          case Right(e: B) => Some(e)
          case Left(err) =>
            logger.warn(s"failed to process $err")
            None
        }
        targetDb.run(DBIO.sequence(insert(toInsert)))
      }
    } yield inserted

  }

  def align(sourceDb: SQLiteProfile.backend.Database,
            targetDb: SQLiteProfile.backend.Database): Future[Seq[Int]] = {
    val url =
      "http://lh3.googleusercontent.com/112k-9-NflCZLN-V40c-viTCUamyzGzNPCmwtnlFaSCUAYfGdhESqqj0OhDuxwop8NMmLd1Q35ClHCPTqLt-"
    transform(sourceDb,
              targetDb,
              TpsTables.tpsQuery
                .filter(_.photo === url)
                .filter(_.formType === FormType.PPWP.value)
                .result,
              alignPhoto,
              ResultsTables.upsertAlign)
  }

  def extract(sourceDb: SQLiteProfile.backend.Database,
              targetDb: SQLiteProfile.backend.Database): Future[Seq[Int]] =
    transform(sourceDb,
              targetDb,
              ResultsTables.alignResultsQuery.result,
              extractNumbers,
              ResultsTables.upsertExtract)

  def processProbabilities(sourceDb: SQLiteProfile.backend.Database,
                           targetDb: SQLiteProfile.backend.Database): Future[Seq[Int]] =
    transform(sourceDb,
              targetDb,
              ResultsTables.extractResultsQuery.result,
              processProbabilities,
              ResultsTables.upsertPresidential)

  def alignPhoto(tps: Seq[SingleTps]): Future[Seq[Either[String, AlignResult]]] = {
    Future
      .sequence(tps.map { tps: SingleTps =>
        val photo: Array[String] = tps.photo.split("/")
        val photoUrl             = photo(photo.length - 1)
        val formType             = tps.verification.c1.get.`type`
        val formConfig           = kawalc1.formTypeToConfig(formType)
        client.alignPhoto(tps.kelurahanId, tps.tpsId, photoUrl, ImageSize, formConfig).map {
          case Right(t) =>
            t.transformedUrl match {
              case Some(trans) =>
                Right(
                  AlignResult(tps.kelurahanId,
                              tps.tpsId,
                              tps.photo,
                              ImageSize,
                              100,
                              formConfig,
                              Some(trans),
                              None))
              case None =>
                Right(
                  AlignResult(tps.kelurahanId,
                              tps.tpsId,
                              tps.photo,
                              ImageSize,
                              0,
                              formConfig,
                              None,
                              None))
            }
          case Left(str) => Left(str)
        }
      })
  }

  private def extractNumbers(
      results: Seq[AlignResult]): Future[Seq[Either[String, ExtractResult]]] = {
    Future
      .sequence(results.map { res: AlignResult =>
        val alignedLastSegment = res.alignedUrl.get.split("/")
        val alignedFileName    = alignedLastSegment(alignedLastSegment.length - 1)
        for {
          extracted <- client.extractNumbers(res.id, res.tps, alignedFileName, res.config)
        } yield {
          extracted match {
            case Right(e: Extraction) =>
              Right(
                ExtractResult(res.id,
                              res.tps,
                              res.photo,
                              Serialization.write(e),
                              res.config,
                              e.digitArea,
                              ""))
            case Left(str) => Left(str)
          }
        }
      })

  }

  private def processProbabilities(
      results: Seq[ExtractResult]): Future[Seq[Either[String, PresidentialResult]]] = {
    Future
      .sequence(results.map { res: ExtractResult =>
        for {
          extracted <- {
            val extraction = Serialization.read[Extraction](res.response)
            client.processProbabilities(res.id, res.tps, extraction.numbers, res.config)
          }
        } yield {
          extracted match {
            case Right(p: ProbabilitiesResponse) =>
              val first  = p.probabilityMatrix.head.head
              val second = p.probabilityMatrix.tail.head.head

              val pas1            = first.numbers.filter(_.shortName == "jokowi").head.number
              val pas2            = first.numbers.filter(_.shortName == "prabowo").head.number
              val jumlahCalon     = first.numbers.filter(_.shortName == "jumlah").head.number
              val calonConfidence = first.confidence

              val jumlah           = second.numbers.filter(_.shortName == "jumlah").head.number
              val tidakSah         = second.numbers.filter(_.shortName == "tidakSah").head.number
              val jumlahSeluruh    = second.numbers.filter(_.shortName == "jumlahSeluruh").head.number
              val jumlahConfidence = second.confidence

              Right(
                PresidentialResult(
                  id = res.id,
                  tps = res.tps,
                  photo = res.photo,
                  response = "resp",
                  pas1 = pas1,
                  pas2 = pas2,
                  jumlahCalon = jumlahCalon,
                  calonConfidence = calonConfidence,
                  jumlahSah = jumlah,
                  tidakSah = tidakSah,
                  jumlahSeluruh = jumlahSeluruh,
                  jumlahConfidence = jumlahConfidence
                ))
            case Left(str) => Left(str)
          }
        }
      })

  }
}
