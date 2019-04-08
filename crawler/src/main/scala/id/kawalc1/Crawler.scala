package id.kawalc1

import akka.actor.ActorSystem
import akka.stream.ActorMaterializer
import com.typesafe.scalalogging.LazyLogging
import id.kawalc1.clients.{KawalC1Client, KawalPemiluClient}
import id.kawalc1.database.{
  AlignResult,
  ExtractResult,
  PresidentialResult,
  ResultsTables,
  TpsTables
}
import id.kawalc1.services.{PhotoProcessor, TpsFetcher}
import slick.jdbc.SQLiteProfile
import slick.jdbc.SQLiteProfile.api._

import scala.concurrent.duration._
import scala.concurrent.{Await, ExecutionContext}

object Crawler extends App with LazyLogging {

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
  val kelurahanDatabase = Database.forConfig("kelurahanMinimalDatabase")
  val resultsDatabase   = Database.forConfig("verificationResults")

  def createDatabase() = {
    val create = DBIO.seq(TpsTables.tpsQuery.schema.drop, TpsTables.tpsQuery.schema.create)
    tpsDb.run(create)
  }

  val processor = new PhotoProcessor(new KawalC1Client("http://localhost:8000"))

  arg match {
    case "fullSync" =>
      Await.result(createDatabase(), 1.minute)
      Await.result(new TpsFetcher(new KawalPemiluClient("https://kawal-c1.appspot.com/api/c"),
                                  kelurahanDatabase,
                                  tpsDb).ingestAllTps(),
                   1.hour)
    case "align" =>
      val alignment = processor.align(tpsDb, resultsDatabase)
      val res       = Await.result(alignment, 1.hour)
      logger.info(s"Aligned ${res.size} photo(s)")

    case "extract" =>
      val extraction = processor.extract(resultsDatabase, resultsDatabase)
      val res        = Await.result(extraction, 1.hour)
      logger.info(s"Extracted ${res.size} photo(s)")

    case "presidential" =>
      val probs = processor.processProbabilities(resultsDatabase, resultsDatabase)
      val res   = Await.result(probs, 1.hour)
      logger.info(s"Processed ${res.size} presidential result(s)")

    case "createDb" =>
      args(1) match {
        case "results" =>
          val resultsCreate = DBIO.seq(ResultsTables.alignResultsQuery.schema.create)
          Await.result(resultsDatabase.run(resultsCreate), 1.minute)
          logger.info("created results Database")
        case "extract" =>
          val extractCreate = DBIO.seq(ResultsTables.extractResultsQuery.schema.create)
          Await.result(resultsDatabase.run(extractCreate), 1.minute)
          logger.info("created extraction Database")
        case "presidential" =>
          val presidentialCreate = DBIO.seq(ResultsTables.presidentialResultsQuery.schema.create)
          Await.result(resultsDatabase.run(presidentialCreate), 1.minute)
          logger.info("created presidential Database")
      }
  }
  system.terminate()

}
