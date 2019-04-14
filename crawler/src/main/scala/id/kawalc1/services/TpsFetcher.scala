package id.kawalc1.services
import akka.NotUsed
import akka.stream.Materializer
import akka.stream.scaladsl.{ Source => StreamSource }
import com.typesafe.scalalogging.LazyLogging
import id.kawalc1
import id.kawalc1.Kelurahan
import id.kawalc1.clients.{ KawalPemiluClient, Response }
import id.kawalc1.database.TpsTables
import slick.jdbc.SQLiteProfile
import slick.jdbc.SQLiteProfile.api._

import scala.concurrent.ExecutionContext.Implicits.global
import scala.concurrent.duration._
import scala.concurrent.{ Await, Future }

trait BlockingSupport {

  def duration = 30.seconds

  implicit def fh[T](f: Future[T]): Object {
    def futureValue: T
  } = new {
    def futureValue: T = Await.result(f, duration)
  }

}
class TpsFetcher(
  client: KawalPemiluClient,
  kelurahanDb: SQLiteProfile.backend.Database,
  tpsDb: SQLiteProfile.backend.Database)(implicit mat: Materializer)
  extends LazyLogging
  with BlockingSupport {
  val Paralellism = 10

  def ingestAllTps() = {
    fetchNext(start = 44000, limit = 500)
  }

  def fetchNext(start: Int, limit: Int): Future[Unit] = {
    fetchBatch(start, limit).map {
      case 0 =>
        logger.info(s"Fetching finished")
        Future.unit
      case x =>
        logger.info(s"Fetching $start - ${start + limit}")
        fetchNext(start + limit, limit)
    }
  }

  private def fetchBatch(start: Int, limit: Int): Future[Int] = {
    for {
      tpses <- kelurahanDb.run(TpsTables.kelurahanQuery.drop(start).take(limit).result)
      fetched <- fetchTpses(tpses.toList)
      stored <- tpsDb.run(TpsTables.tpsQuery ++= fetched)
    } yield {
      tpses.size
    }
  }

  def fetchTpses(kelurahan: List[kawalc1.KelurahanId]) = {
    val futures: StreamSource[Either[Response, kawalc1.Kelurahan], NotUsed] =
      StreamSource(kelurahan)
        .mapAsync(Paralellism)({ lurah =>
          client.getKelurahan(lurah.idKel)
        })

    val accumulated = futures.runFold(Seq.empty[Either[Response, kawalc1.Kelurahan]])(_ :+ _)
    accumulated.map(_.flatMap {
      case Right(kel) => Some(Kelurahan.toTps(kel))
      case Left(err) =>
        logger.warn(s"Failed to fetch $err")
        None
    }.flatten)
  }
}
