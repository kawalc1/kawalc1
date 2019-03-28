package id.kawalc1

import java.sql.Timestamp

import com.typesafe.scalalogging.LazyLogging
import id.kawalc1.database.Tables
import org.scalatest.{Matchers, WordSpec}
import slick.jdbc.H2Profile.api._

import scala.language.reflectiveCalls

class DatabaseSpecs extends WordSpec with Matchers with FutureMatcher with LazyLogging {
  "Database" should {
    "Store TPS results" in {
      val db = Database.forConfig("tpsTestDatabase")
      val testTps = SingleTps("http://somewhere/photo.jpg", 1, 1, Verification(Timestamp.valueOf("2019-03-01 00:00:00"), None, None))
      val setup = DBIO.seq(
        Tables.tpsQuery.schema.create,
        Tables.tpsQuery += testTps
      )
      try {
        db.run(setup).futureValue
        val tpses = db.run(Tables.tpsQuery.result).futureValue
        tpses.head shouldBe testTps
      } finally db.close()
    }
  }
}
