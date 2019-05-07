package id.kawalc1

import java.io.{ File, PrintWriter }
import java.net.URL
import java.time.LocalDateTime

import akka.actor.ActorSystem
import akka.stream.ActorMaterializer
import com.typesafe.scalalogging.LazyLogging
import id.kawalc1.Config.Application
import id.kawalc1.cli.{ CrawlerConf, Tool }
import id.kawalc1.clients.{ JsonSupport, KawalC1Client, KawalPemiluClient }
import id.kawalc1.database.{ AlignResult, DetectionResult, ResultsTables, TpsTables }
import id.kawalc1.services.{ BlockingSupport, PhotoProcessor }
import org.json4s.native.Serialization
import slick.{ backend, jdbc }
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
    conf.Submit,
    (c: CrawlerConf) => {
      val token = c.Submit.token.toOption.get
      val force = c.Submit.force.toOption.getOrElse(false)
      val problems: Seq[Problem] = resultsDatabase.run(ResultsTables.problemsToReportQuery.result).futureValue

      problems.foreach {
        x =>
          println(s"problem $x")

          val success = kawalPemiluClient.subitProblem("https://upload.kawalpemilu.org", token, x).futureValue
          Thread.sleep(400)
          success match {
            case Right(submitted) =>
              val reported = ProblemReported(x.kelId, "", x.tpsNo, x.url, x.reason)
              resultsDatabase.run(ResultsTables.problemsReportedQuery.insertOrUpdate(reported)).futureValue
            case Left(err) =>
              println(s"Error: $err")
              resultsDatabase.run(ResultsTables.problemsQuery.insertOrUpdate(x.copy(response_code = Some(err.code)))).futureValue
          }
        //        println(s"$success")
      }

    })

  myTool.registerSubcmdHandler(
    conf.Stats,
    (c: CrawlerConf) => {
      val on = c.Stats.on()
      on match {
        case "det-duplicated" =>
          val aligned = resultsDatabase.run(ResultsTables.detectionsQuery.result).futureValue
          val grouped: Map[String, Seq[DetectionResult]] = aligned.groupBy((x: DetectionResult) => s"${x.hash.getOrElse("")}")
          println(s"Groups size: ${grouped.size}")
          val pw = new PrintWriter(new File("scan-dups.csv"))
          val duplicates = grouped.filter {
            case (hash, group: Seq[DetectionResult]) =>
              val details = group.map(x => s"${x.kelurahan},${x.tps}").toSet

              if (details.size > 1 && hash != "" && hash != "hash") {
                val jumlahSet = group.map(x => s"${x.jumlah},${x.php_jumlah}").toSet
                if (jumlahSet.size == 1) {
                  grouped(hash).foreach { x: DetectionResult =>
                    pw.println(s"${x.photo},${x.kelurahan},${x.tps},${details.size},$hash")
                  }
                }

              }
              group.size > 1
          }
          pw.close()
          //              if (group.size > 1) println(s"${details.head},${group.size},https://upload.kawalpemilu.org/t/${group.head.id}")
          //              group.size > 1 //&& group.map(x => s"${x.id},${x.tps}").toSet.size > 1

          println(s"Size ${duplicates.size}")
        case "duplicates" =>
          val aligned = resultsDatabase.run(ResultsTables.alignResultsQuery.result).futureValue
          val grouped: Map[String, Seq[AlignResult]] = aligned.groupBy((x: AlignResult) => s"${x.hash.getOrElse("")}")
          val pw = new PrintWriter(new File("photo-dups.csv"))
          val duplicates: Map[String, Seq[AlignResult]] = grouped.filter {
            case (hash: String, group: Seq[AlignResult]) =>
              val details = group.map(x => s"${x.id},${x.tps}").toSet

              if (details.size > 1 && hash != "" && hash != "hash") {
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
        case "problems" =>
          createDb(ResultsTables.problemsQuery.schema, resultsDatabase, drop)
        case "problems-reported" =>
          createDb(ResultsTables.problemsReportedQuery.schema, resultsDatabase, drop)
        case "forms-processed" =>
          createDb(ResultsTables.formsProcessedQuery.schema, resultsDatabase, drop)
        case "detect" =>
          createDb(ResultsTables.detectionsQuery.schema, resultsDatabase, drop)
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
      val service = c.Process.service.toOption.getOrElse(Application.kawalC1UrlLocal)
      val batchParams = BatchParams(offset, batchSize, threads, limit)
      val kawalC1Client = new KawalC1Client(service)
      val url = new URL(service)
      logger.info(s"Starting $phase with ${Serialization.write(batchParams)}")
      phase match {
        case "test" =>
          val howMany = resultsDatabase.run(ResultsTables.tpsToDetectQuery(Plano.NO).result).futureValue.length
          println(s"This much: $howMany")
        case "fetch" =>
          process("fetch", processor.fetch, kelurahanDatabase, resultsDatabase, kawalC1Client, batchParams)
        case "align" =>
          val howMany = resultsDatabase.run(ResultsTables.tpsToAlignQuery(Plano.NO).result).futureValue.length
          logger.info(s"Will align $howMany forms")
          process("align", processor.align, resultsDatabase, resultsDatabase, kawalC1Client, batchParams)
        case "extract" =>
          val howMany = resultsDatabase.run(ResultsTables.tpsToExtractQuery.result).futureValue.length
          logger.info(s"Will extract $howMany forms with $batchParams")
          process("extract", processor.extract, resultsDatabase, resultsDatabase, kawalC1Client, batchParams)
        case "presidential" =>
          process("presidential", processor.processProbabilities, resultsDatabase, resultsDatabase, kawalC1Client, batchParams)
        case "detect" =>
          implicit val pw = new PrintWriter(new File(s"batches/detections-${LocalDateTime.now()}-${url.getHost}.csv"))
          val howMany = resultsDatabase.run(ResultsTables.tpsToDetectQuery(Plano.NO).result).futureValue.length
          println(s"Will detect: $howMany")
          process("detections", processor.processDetections, resultsDatabase, resultsDatabase, kawalC1Client, batchParams)
        case "roi" =>
          implicit val pw = new PrintWriter(new File(s"batches/rois-${LocalDateTime.now()}-${url.getHost}.csv"))
          val howMany = resultsDatabase.run(ResultsTables.tpsToRoiQuery.result).futureValue.length
          println(s"Will detect: $howMany")
          process("rois", processor.processRois, resultsDatabase, resultsDatabase, kawalC1Client, batchParams)
      }
    })
  myTool.run()
  system.terminate()
}
