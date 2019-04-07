package id.kawalc1.services

import id.kawalc1
import id.kawalc1.{ProbabilitiesResponse, SingleTps}
import id.kawalc1.clients.{Extraction, JsonSupport, KawalC1Client, Probabilities}
import id.kawalc1.database.{AlignResult, ExtractResult, PresidentialResult}
import org.json4s.native.Serialization

import scala.concurrent.{ExecutionContext, Future}

case class AlignedPicture(url: String, imageSize: Int)

class PhotoProcessor(client: KawalC1Client)(implicit val ex: ExecutionContext) extends JsonSupport {

  val ImageSize = 1280

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

  def extractNumbers(results: Seq[AlignResult]): Future[Seq[Either[String, ExtractResult]]] = {
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

  def processProbabilities(
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
