#include "log.h"
#include "stdafx.h"

Logger* logger;

Logger::Logger(std::string filename)
{
	if(!StartNewLogFile(filename))
		throw g5Exception("log", "could not open log file", false);
}

//i suggest an html file
bool Logger::StartNewLogFile(std::string filename)
{
	//overwrite and open file
	m_Filename = filename;
	m_File.open(filename.c_str());
	
	if(!m_File.is_open())
		return false;

	m_File<<"<html><head><title>C1 LOG</title></head><body width=\"1024\"><font size=\"+1\"><b>Log file opened</b></font><br><br>\n\n";
	return true;
}

void Logger::Log(LOGTYPE type, char* file, int line, const char* function, const std::string& logstring)
{
	switch(type)
	{
	case LOG_SUCCESS:
		m_File<<"<font color=\"blue\">SUCCESS  "<<file<<"("<<line<<")"<<function<<" - <pre>"<<logstring<<"</pre></font><br>\n";
		break;
	case LOG_INFORMATION:
		m_File<<"<font color=\"grey\">"<<file<<"("<<line<<")"<<function<<" - <pre>"<<logstring<<"</pre></font><br>\n";
		break;
	case LOG_WARNING:
		m_File<<"<font color=\"orange\"><b>WARNING  </b>"<<file<<"("<<line<<")"<<function<<" - <pre>"<<logstring<<"</pre></font><br>\n";
		break;
	case LOG_ERROR:
		m_File<<"<font color=\"red\" size=\"+1\"><b>ERROR  "<<file<<"("<<line<<")"<<function<<" - <pre>"<<logstring<<"</pre></b></font><br>\n";
		break;
	default:
		return;
	}
	cout << logstring << endl;
	m_File.flush();
}

Logger::~Logger()
{
	m_File<<"<br><font size=\"+1\"><b>Log file closed</b></font><br>\n\n</body></html>";
	m_File.close();
}
