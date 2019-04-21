package id.kawalc1

import java.io.{ File, PrintWriter }

import akka.actor.ActorSystem
import akka.stream.ActorMaterializer
import com.typesafe.scalalogging.LazyLogging
import id.kawalc1.Config.Application
import id.kawalc1.cli.{ CrawlerConf, Tool }
import id.kawalc1.clients.{ JsonSupport, KawalC1Client, KawalPemiluClient }
import id.kawalc1.database.{ AlignResult, ResultsTables, TpsTables }
import id.kawalc1.services.{ BlockingSupport, PhotoProcessor }
import org.json4s.native.Serialization
import slick.jdbc
import slick.jdbc.SQLiteProfile
import slick.jdbc.SQLiteProfile.api._

import scala.concurrent.ExecutionContext
import scala.concurrent.duration._
import scala.language.reflectiveCalls

case class BatchParams(start: Long, batchSize: Long, threads: Int, limit: Option[Int])

object Crawler extends App with LazyLogging with BlockingSupport with JsonSupport {
  override def duration: FiniteDuration = 1.hour

  implicit val system: ActorSystem = ActorSystem("crawler")
  implicit val materializer: ActorMaterializer = ActorMaterializer()
  implicit val executionContext: ExecutionContext = system.dispatcher

  val conf = new CrawlerConf(args.toSeq)
  val myTool = new Tool(conf)

  private val localKawalC1 = new KawalC1Client(Application.kawalC1UrlLocal)
  private val alternativeLocalKawalC1 = new KawalC1Client(Application.kawalC1AlternativeUrlLocal)
  private val remoteKawalC1 = new KawalC1Client(Application.kawalC1Url)
  private val kawalPemiluClient = new KawalPemiluClient("https://kawal-c1.appspot.com/api/c")
  val processor =
    new PhotoProcessor(kawalPemiluClient)
  val tpsDb = Database.forConfig("tpsDatabase")
  val kelurahanDatabase = Database.forConfig("kelurahanDatabase")
  val resultsDatabase = Database.forConfig("verificationResults")

  def process(
    phase: String,
    func: (SQLiteProfile.backend.Database, SQLiteProfile.backend.Database, KawalC1Client, BatchParams) => Long,
    sourceDb: SQLiteProfile.backend.Database,
    targetDb: SQLiteProfile.backend.Database,
    client: KawalC1Client,
    params: BatchParams): Unit = {
    val amount = func(sourceDb, targetDb, client, params)
    logger.info(s"Processed $amount in phase $phase")
  }

  def createDb(schema: jdbc.SQLiteProfile.SchemaDescription, database: SQLiteProfile.backend.Database, drop: Boolean = false): Unit = {
    val action = if (drop) {
      DBIO.seq(schema.drop, schema.create)
    } else {
      DBIO.seq(schema.create)
    }
    database
      .run(action)
      .map { _ =>
        logger.info(s"created Database \n ${schema.createStatements.toSeq.mkString("\n")}")
      }
      .futureValue
  }

  myTool.registerSubcmdHandler(
    conf.Stats,
    (c: CrawlerConf) => {
      val on = c.Stats.on()
      on match {
        case "duplicates" =>
          val aligned = resultsDatabase.run(ResultsTables.alignResultsQuery.result).futureValue
          val grouped: Map[String, Seq[AlignResult]] = aligned.groupBy((x: AlignResult) => s"${x.hash.getOrElse("")}")
          val pw = new PrintWriter(new File("dups.csv"))
          val duplicates: Map[String, Seq[AlignResult]] = grouped.filter {
            case (hash, group: Seq[AlignResult]) =>
              val details = group.map(x => s"${x.id},${x.tps}").toSet

              if (details.size > 1) {
                grouped(hash).foreach { x: AlignResult =>
                  val first = group.head
                  val foto = first.photo
                  pw.println(s"${x.photo},${x.id},${x.tps},${details.size},$hash")
                }

              }
              group.size > 1
          }
          pw.close()
          //              if (group.size > 1) println(s"${details.head},${group.size},https://upload.kawalpemilu.org/t/${group.head.id}")
          //              group.size > 1 //&& group.map(x => s"${x.id},${x.tps}").toSet.size > 1

          println(s"Size ${duplicates.size}")
      }
    })
  myTool.registerSubcmdHandler(
    conf.CreateDb,
    (c: CrawlerConf) => {
      val phase = c.CreateDb.name
      val drop = c.CreateDb.drop()
      phase() match {
        case "fetch" =>
          createDb(TpsTables.tpsQuery.schema, resultsDatabase, drop)
        case "align" =>
          createDb(ResultsTables.alignResultsQuery.schema, resultsDatabase, drop)
        case "extract" =>
          createDb(ResultsTables.extractResultsQuery.schema, resultsDatabase, drop)
        case "presidential" =>
          createDb(ResultsTables.presidentialResultsQuery.schema, resultsDatabase, drop)
      }
    })

  val urlie = "http://lh3.googleusercontent.com/6TSO9UKWsCHekURjdjoWOEKwYbUjUUsWUJqYVB_3VWVmm9TLvfoaXbPXLmgE8p0PbQtsEQ1OFaDC0FRSMbw"
  myTool.registerSubcmdHandler(
    conf.Process,
    (c: CrawlerConf) => {
      val phase = c.Process.phase()
      val offset = c.Process.offset.toOption.getOrElse(0)
      val batchSize = c.Process.batch.toOption.getOrElse(50)
      val threads = c.Process.threads.toOption.getOrElse(10)
      val limit = c.Process.limit.toOption
      val batchParams = BatchParams(offset, batchSize, threads, limit)
      logger.info(s"Starting $phase with ${Serialization.write(batchParams)}")
      phase match {
        case "test" =>
          val howMany = resultsDatabase.run(ResultsTables.alignErrorQuery.result).futureValue.length
          println(s"This much: $howMany")
        case "fetch" =>
          process("fetch", processor.fetch, kelurahanDatabase, resultsDatabase, localKawalC1, batchParams)
        case "align" =>
          val howMany = resultsDatabase.run(ResultsTables.tpsToAlignQuery(Plano.NO).result).futureValue.length
          logger.info(s"Will align $howMany forms")
          process("align", processor.align, resultsDatabase, resultsDatabase, remoteKawalC1, batchParams)
        case "extract" =>
          val howMany = resultsDatabase.run(ResultsTables.tpsToExtractQuery.result).futureValue.length
          logger.info(s"Will extract $howMany forms with $batchParams")
          process("extract", processor.extract, resultsDatabase, resultsDatabase, localKawalC1, batchParams)
        case "presidential" =>
          process("presidential", processor.processProbabilities, resultsDatabase, resultsDatabase, alternativeLocalKawalC1, batchParams)
      }
    })
  myTool.run()
  system.terminate()
}
