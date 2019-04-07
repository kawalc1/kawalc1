package id.kawalc1.services
import java.util.concurrent.TimeUnit

import akka.NotUsed
import akka.stream.Materializer
import id.kawalc1
import id.kawalc1.clients.KawalPemiluClient
import id.kawalc1.database.TpsTables
import slick.jdbc.SQLiteProfile.api._
import akka.stream.scaladsl.{ Source => StreamSource }
import com.typesafe.scalalogging.LazyLogging
import id.kawalc1.Kelurahan
import slick.jdbc.SQLiteProfile

import scala.concurrent.ExecutionContext.Implicits.global
import scala.concurrent.duration.Duration
import scala.concurrent.{ Await, Future }

trait BlockingSupport {

  implicit def fh[T](f: Future[T]): Object {
    def futureValue: T
  } = new {
    def futureValue: T = Await.result(f, Duration(30, TimeUnit.SECONDS))
  }

}
class TpsFetcher(
  client: KawalPemiluClient,
  kelurahanDb: SQLiteProfile.backend.Database,
  tpsDb: SQLiteProfile.backend.Database)(implicit mat: Materializer)
  extends LazyLogging
  with BlockingSupport {
  val Paralellism = 20

  def ingestAllTps() = {
    for {
      tpses <- kelurahanDb.run(TpsTables.kelurahanQuery.result)
      fetched <- fetchTpses(tpses.toList)
      stored <- tpsDb.run(TpsTables.tpsQuery ++= fetched)
    } yield stored
  }

  def fetchTpses(kelurahan: List[kawalc1.KelurahanId]) = {
    val futures: StreamSource[Either[String, kawalc1.Kelurahan], NotUsed] =
      StreamSource(kelurahan)
        .mapAsync(Paralellism)({ lurah =>
          client.getKelurahan(lurah.idKel)
        })

    val accumulated = futures.runFold(Seq.empty[Either[String, kawalc1.Kelurahan]])(_ :+ _)
    accumulated.map(_.flatMap {
      case Right(kel) => Some(Kelurahan.toTps(kel))
      case Left(err) =>
        logger.warn(s"Failed to fetch $err")
        None
    }.flatten)
  }
}
