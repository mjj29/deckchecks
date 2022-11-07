import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { ITable } from "./table.api";

@Injectable({
        providedIn: 'root'
})
export class TableService {

        constructor(private http: HttpClient) { }

        private _url: string = "/rest/table/";

        getTable(event: bigint, table: bigint): Observable<ITable> {
                return this.http.get<ITable>("/"+event+this._url+table).pipe(catchError(this.errorHandler));
        }

        errorHandler(error: HttpErrorResponse) {
                return throwError(error.message || "Server Error");
        }
}
