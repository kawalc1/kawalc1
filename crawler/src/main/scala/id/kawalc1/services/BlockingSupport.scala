package id.kawalc1.services

import scala.concurrent.{Await, Future}
import scala.concurrent.duration._
import scala.language.implicitConversions

trait BlockingSupport {

  def duration: FiniteDuration = 30.seconds

  implicit def fh[T](f: Future[T]): Object {
    def futureValue: T
  } = new {
    def futureValue: T = Await.result(f, duration)
  }

}
