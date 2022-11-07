import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { ITop } from "./top.api";

@Injectable({
        providedIn: 'root'
})
export class TopService {

        constructor(private http: HttpClient) { }

        private _url: string = "/rest/top/";

        getTop(event: int): Observable<ITop> {
                return this.http.get<ITop>("/"+event+this._url).pipe(catchError(this.errorHandler));
        }

        errorHandler(error: HttpErrorResponse) {
                return throwError(error.message || "Server Error");
        }
}
