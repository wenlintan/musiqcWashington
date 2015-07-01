#ifndef LOG__H
#define LOG__H

#include <string>
#include <fstream>

enum LOGTYPE { LOG_INFORMATION = 0, LOG_WARNING, LOG_ERROR, LOG_SUCCESS };

class Logger
{
private:
	std::string		m_Filename;
	std::ofstream	m_File;

public:
	Logger(std::string filename);
	~Logger();

	//will leave old file as is and all future comments will go to new file...why the hell would I use this?
	bool StartNewLogFile(std::string filename);

	void Log(LOGTYPE type, char* file, int line, const char* function, const std::string& logstring);
};

extern Logger* logger;

#if(1)
#define LOG_SUCCESS(x) logger->Log(LOG_SUCCESS,__FILE__, __LINE__, __FUNCTION__, x)
#define LOG_INFO(x) logger->Log(LOG_INFORMATION, __FILE__, __LINE__,  __FUNCTION__, x)
#define LOG_WARN(x) logger->Log(LOG_WARNING, __FILE__, __LINE__,  __FUNCTION__, x)
#define LOG_ERR(x) logger->Log(LOG_ERROR, __FILE__, __LINE__,  __FUNCTION__, x)
#else
#define LOG_SUCCESS(x)
#define LOG_INFO(x)
#define LOG_WARN(x)
#define LOG_ERR(x) logger->Log(LOG_ERROR, __FILE__, __LINE__,  __FUNCTION__, x)
#endif

#endif
