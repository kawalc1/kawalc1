package id.kawalc1

import akka.actor.ActorSystem
import akka.stream.ActorMaterializer
import com.typesafe.scalalogging.LazyLogging
import id.kawalc1.clients.{KawalC1Client, KawalPemiluClient}
import id.kawalc1.database.{ResultsTables, TpsTables}
import id.kawalc1.services.{BlockingSupport, PhotoProcessor, TpsFetcher}
import slick.jdbc.SQLiteProfile.api._

import scala.concurrent.ExecutionContext
import scala.concurrent.duration._

object Crawler extends App with LazyLogging with BlockingSupport {
  override def duration: FiniteDuration = 1.hour

  implicit val system: ActorSystem                = ActorSystem("crawler")
  implicit val materializer: ActorMaterializer    = ActorMaterializer()
  implicit val executionContext: ExecutionContext = system.dispatcher

  if (args.isEmpty) {
    println("Usage")
    println("Crawler fullSync|align|(createDb results|extract)")
    System.exit(0)
  }
  val arg = args(0)

  val tpsDb             = Database.forConfig("tpsDatabase")
  val kelurahanDatabase = Database.forConfig("kelurahanDatabase")
  val resultsDatabase   = Database.forConfig("verificationResults")

  def createDatabase() = {
    val create = DBIO.seq(TpsTables.tpsQuery.schema.drop, TpsTables.tpsQuery.schema.create)
    tpsDb.run(create)
  }

  val processor = new PhotoProcessor(new KawalC1Client("http://localhost:8000"))

  arg match {
    case "fullSync" =>
      //        Await.result(createDatabase(), 1.minute)
      new TpsFetcher(new KawalPemiluClient("https://kawal-c1.appspot.com/api/c"),
                     kelurahanDatabase,
                     tpsDb).ingestAllTps().futureValue
    case "align" =>
      processor
        .align(tpsDb, resultsDatabase)
        .map { res =>
          logger.info(s"Aligned ${res.size} photo(s)")
        }
        .futureValue
    case "extract" =>
      processor
        .extract(resultsDatabase, resultsDatabase)
        .map { res =>
          logger.info(s"Extracted ${res.size} photo(s)")
        }
        .futureValue

    case "presidential" =>
      processor
        .processProbabilities(resultsDatabase, resultsDatabase)
        .map { res =>
          logger.info(s"Processed ${res.size} presidential result(s)")
        }
        .futureValue

    case "createDb" =>
      args(1) match {
        case "align" =>
          val resultsCreate = DBIO.seq(ResultsTables.alignResultsQuery.schema.drop,
                                       ResultsTables.alignResultsQuery.schema.create)
          resultsDatabase
            .run(resultsCreate)
            .map { _ =>
              logger.info("created results Database")
            }
            .futureValue
        case "extract" =>
          val extractCreate = DBIO.seq(ResultsTables.extractResultsQuery.schema.drop,
                                       ResultsTables.extractResultsQuery.schema.create)
          resultsDatabase
            .run(extractCreate)
            .map { _ =>
              logger.info("created extraction Database")
            }
            .futureValue
        case "presidential" =>
          val presidentialCreate = DBIO.seq(ResultsTables.presidentialResultsQuery.schema.drop,
                                            ResultsTables.presidentialResultsQuery.schema.create)
          resultsDatabase
            .run(presidentialCreate)
            .map { _ =>
              logger.info("created presidential Database")
            }
            .futureValue
      }
      system.terminate()
  }

}
