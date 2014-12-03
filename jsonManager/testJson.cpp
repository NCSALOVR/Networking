#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"
#include <sstream>
#include <iostream>
#include <fstream>

int main(int argc, char* argv[]) { 

    std::stringstream ss;
    std::ifstream ifs;
    ifs.open("testJsonMain.json", std::ios::binary);
    ss << ifs.rdbuf();
    ifs.close();

    rapidjson::Document docMain;
    docMain.Parse(ss.str().c_str());

    const char* updateJson = "{\"source2\":[{\"x\":1.8, \"z\":2.8},{\"x\":3.8, \"y\":4.8}]}";
    rapidjson::Document docUpd;
    docUpd.Parse(updateJson);

    for (rapidjson::Value::ConstMemberIterator itr = docUpd.MemberBegin(); itr != docUpd.MemberEnd(); ++itr){
        const char* source = itr->name.GetString();
        if(docMain.HasMember(source)){
            rapidjson::Value& arrElemsMain = docMain[source];
            const rapidjson::Value& arrElems = docUpd[source];

            for (rapidjson::SizeType i = 0; i < arrElems.Size(); i++){
                const rapidjson::Value& currPoint = arrElems[i];
                for (rapidjson::Value::ConstMemberIterator itrInner = currPoint.MemberBegin(); itrInner != currPoint.MemberEnd(); ++itrInner){
                    const char* dim = itrInner->name.GetString();
                    std::cout << dim << std::endl;

                    if(arrElemsMain[i].HasMember(dim)){
                        arrElemsMain[i][dim].SetDouble(currPoint[dim].GetDouble());
                    }
                    else{
                        arrElemsMain[i].AddMember(rapidjson::Value(dim, docMain.GetAllocator()).Move(), rapidjson::Value().SetDouble(currPoint[dim].GetDouble()), docMain.GetAllocator());
                    }

                }
            }
        }
    }

    rapidjson::StringBuffer buffer;
    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
    docMain.Accept(writer);

    std::ofstream outputFile;
    outputFile.open("testJsonMainChanged.json");
    outputFile << buffer.GetString();
    outputFile.close();
    std::cout << buffer.GetString() << std::endl;

    return 0;
}
